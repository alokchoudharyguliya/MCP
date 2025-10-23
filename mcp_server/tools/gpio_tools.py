from __future__ import annotations
import json, base64
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator

from ..ssh_transport import SSHClientWrapper
from .common import TargetedRequest, use_client
from ..config import load_config

# Validation helpers
SAFE_MODE = {"BCM", "BOARD"}
SAFE_DIRECTION = {"in", "out"}
SAFE_PULL = {"up", "down", "off"}

def _b64(obj: Dict[str, Any]) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")

def _get_gpio_policy(target: str) -> Dict[str, Any]:
    # Load policies directly since GPIO config is in policies.yaml
    from ..config import load_policies
    policies = load_policies()
    
    # Check if policies has gpio config
    if hasattr(policies, 'gpio') and policies.gpio and hasattr(policies.gpio, 'targets'):
        gpio_cfg = policies.gpio.targets.get(target, {})
        return gpio_cfg
    
    # Return empty config if no GPIO policy found
    return {}

def _validate_pin(target: str, pin: int, mode: str, needed_cap: str):
    pol = _get_gpio_policy(target)
    if not pol:
        raise ValueError(f"GPIO policy missing for target {target}")
    default_mode = pol.get("default_mode", "BCM").upper()
    mode = (mode or default_mode).upper()
    if mode not in SAFE_MODE:
        raise ValueError("mode must be BCM or BOARD")
    allowed_map = pol.get("allowed_pins", {})
    allowed = allowed_map.get(mode, [])
    if int(pin) not in [int(p) for p in allowed]:
        raise ValueError(f"pin {pin} not allowed for mode {mode}")
    caps = pol.get("capabilities", {})
    c = set(caps.get(str(pin), []))
    if needed_cap not in c:
        raise ValueError(f"pin {pin} lacks capability '{needed_cap}' (has: {sorted(list(c))})")
    return mode, pol

class GPIOWriteRequest(TargetedRequest):
    pin: int
    value: int | bool = Field(description="0/1 or false/true")
    mode: Optional[str] = Field(default=None, description="BCM or BOARD; default from policy")
    direction: str = Field(default="out", description="Force direction; must be 'out'")
    pull: Optional[str] = Field(default=None, description="up/down/off for input mode (ignored for out)")

    @validator("direction")
    def _val_dir(cls, v):
        if v not in SAFE_DIRECTION:
            raise ValueError("direction must be 'in' or 'out'")
        return v

    @validator("mode")
    def _val_mode(cls, v):
        if v is None: return v
        if v.upper() not in SAFE_MODE:
            raise ValueError("mode must be BCM or BOARD")
        return v.upper()

class GPIOSimpleResponse(BaseModel):
    ok: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def gpio_write(req: GPIOWriteRequest) -> GPIOSimpleResponse:
    mode, pol = _validate_pin(req.target, int(req.pin), req.mode or "", "write")
    payload = {
        "op": "write",
        "data": {
            "pin": int(req.pin),
            "value": 1 if (req.value is True or int(req.value) == 1) else 0,
            "mode": mode,
            "direction": "out"
        }
    }
    agent = pol.get("agent_path")
    if not agent:
        return GPIOSimpleResponse(ok=False, error="agent_path missing in policy")
    with use_client(req.target) as cli:
        r = cli.exec(f'python3 "{agent}" "{_b64(payload)}"', cwd=".")
        try:
            out = json.loads(r.stdout or "{}")
        except Exception:
            out = {"ok": False, "error": "invalid agent output", "raw": r.stdout}
        if out.get("ok"):
            return GPIOSimpleResponse(ok=True, result=out)
        return GPIOSimpleResponse(ok=False, error=out.get("error") or r.stderr)

TOOL_GPIO_WRITE = {
    "name": "gpio_write",
    "description": "Set a GPIO pin HIGH/LOW.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "pin": {"type": "integer"},
            "value": {"type": ["integer", "boolean"]},
            "mode": {"type": "string"},
            "direction": {"type": "string"},
            "pull": {"type": "string"}
        },
        "required": ["target", "pin", "value"]
    },
    "output_schema": {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "result": {"type": "object"}, "error": {"type": "string"}},
        "required": ["ok"]
    }
}

class GPIOReadRequest(TargetedRequest):
    pin: int
    mode: Optional[str] = None
    direction: str = Field(default="in")
    pull: Optional[str] = None

    @validator("direction")
    def _val_dir(cls, v):
        if v not in SAFE_DIRECTION:
            raise ValueError("direction must be 'in' or 'out'")
        return v

    @validator("mode")
    def _val_mode(cls, v):
        if v is None: return v
        if v.upper() not in SAFE_MODE:
            raise ValueError("mode must be BCM or BOARD")
        return v.upper()

    @validator("pull")
    def _val_pull(cls, v):
        if v is None: return v
        if v not in SAFE_PULL:
            raise ValueError("pull must be up/down/off")
        return v

def gpio_read(req: GPIOReadRequest) -> GPIOSimpleResponse:
    mode, pol = _validate_pin(req.target, int(req.pin), req.mode or "", "read")
    payload = {
        "op": "read",
        "data": {
            "pin": int(req.pin),
            "mode": mode,
            "direction": "in",
            "pull": req.pull
        }
    }
    agent = pol.get("agent_path")
    if not agent:
        return GPIOSimpleResponse(ok=False, error="agent_path missing in policy")
    with use_client(req.target) as cli:
        r = cli.exec(f'python3 "{agent}" "{_b64(payload)}"')
        try:
            out = json.loads(r.stdout or "{}")
        except Exception:
            out = {"ok": False, "error": "invalid agent output", "raw": r.stdout}
        if out.get("ok"):
            return GPIOSimpleResponse(ok=True, result=out)
        return GPIOSimpleResponse(ok=False, error=out.get("error") or r.stderr)

TOOL_GPIO_READ = {
    "name": "gpio_read",
    "description": "Read a GPIO pin.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "pin": {"type": "integer"},
            "mode": {"type": "string"},
            "direction": {"type": "string"},
            "pull": {"type": "string"}
        },
        "required": ["target", "pin"]
    },
    "output_schema": TOOL_GPIO_WRITE["output_schema"]
}

class GPIOPWMRequest(TargetedRequest):
    pin: int
    duty: float = Field(description="0..100")
    freq: float = Field(default=1000.0, description="Hz")
    duration: float = Field(default=0.2, description="Seconds to run then stop (default 0.2s)")
    mode: Optional[str] = None

    @validator("duty")
    def _val_duty(cls, v: float):
        if v < 0 or v > 100:
            raise ValueError("duty must be in [0,100]")
        return v

def gpio_pwm(req: GPIOPWMRequest) -> GPIOSimpleResponse:
    mode, pol = _validate_pin(req.target, int(req.pin), req.mode or "", "pwm")
    payload = {
        "op": "pwm",
        "data": {
            "pin": int(req.pin),
            "duty": float(req.duty),
            "freq": float(req.freq),
            "duration": float(req.duration),
            "mode": mode
        }
    }
    agent = pol.get("agent_path")
    if not agent:
        return GPIOSimpleResponse(ok=False, error="agent_path missing in policy")
    with use_client(req.target) as cli:
        r = cli.exec(f'python3 "{agent}" "{_b64(payload)}"')
        try:
            out = json.loads(r.stdout or "{}")
        except Exception:
            out = {"ok": False, "error": "invalid agent output", "raw": r.stdout}
        if out.get("ok"):
            return GPIOSimpleResponse(ok=True, result=out)
        return GPIOSimpleResponse(ok=False, error=out.get("error") or r.stderr)

TOOL_GPIO_PWM = {
    "name": "gpio_pwm",
    "description": "Run PWM on a GPIO pin for a short duration.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "pin": {"type": "integer"},
            "duty": {"type": "number"},
            "freq": {"type": "number"},
            "duration": {"type": "number"},
            "mode": {"type": "string"}
        },
        "required": ["target", "pin", "duty"]
    },
    "output_schema": TOOL_GPIO_WRITE["output_schema"]
}

# GPIO Blink functionality
class GPIOBlinkRequest(TargetedRequest):
    pin: int
    count: int = Field(default=5, description="Number of blinks")
    on_time: float = Field(default=0.5, description="Seconds LED is ON")
    off_time: float = Field(default=0.5, description="Seconds LED is OFF")
    mode: Optional[str] = Field(default=None, description="BCM or BOARD; default from policy")

    @validator("count")
    def _val_count(cls, v):
        if v < 1:
            raise ValueError("count must be at least 1")
        return v

    @validator("on_time", "off_time")
    def _val_time(cls, v):
        if v < 0:
            raise ValueError("time values must be non-negative")
        return v

    @validator("mode")
    def _val_mode(cls, v):
        if v is None: return v
        if v.upper() not in SAFE_MODE:
            raise ValueError("mode must be BCM or BOARD")
        return v.upper()

def gpio_blink(req: GPIOBlinkRequest) -> GPIOSimpleResponse:
    mode, pol = _validate_pin(req.target, int(req.pin), req.mode or "", "write")
    payload = {
        "op": "blink",
        "data": {
            "pin": int(req.pin),
            "count": int(req.count),
            "on_time": float(req.on_time),
            "off_time": float(req.off_time),
            "mode": mode
        }
    }
    agent = pol.get("agent_path")
    if not agent:
        return GPIOSimpleResponse(ok=False, error="agent_path missing in policy")
    with use_client(req.target) as cli:
        r = cli.exec(f'python3 "{agent}" "{_b64(payload)}"')
        try:
            out = json.loads(r.stdout or "{}")
        except Exception:
            out = {"ok": False, "error": "invalid agent output", "raw": r.stdout}
        if out.get("ok"):
            return GPIOSimpleResponse(ok=True, result=out)
        return GPIOSimpleResponse(ok=False, error=out.get("error") or r.stderr)

TOOL_GPIO_BLINK = {
    "name": "gpio_blink",
    "description": "Blink a GPIO pin (LED) a specified number of times",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target name from config"},
            "pin": {"type": "integer", "description": "GPIO pin number"},
            "count": {"type": "integer", "description": "Number of blinks", "default": 5},
            "on_time": {"type": "number", "description": "Seconds LED is ON", "default": 0.5},
            "off_time": {"type": "number", "description": "Seconds LED is OFF", "default": 0.5},
            "mode": {"type": "string", "description": "GPIO mode (BCM or BOARD)"}
        },
        "required": ["target", "pin"]
    },
    "output_schema": TOOL_GPIO_WRITE["output_schema"]
}

# Macro run: sequence of steps with validation
class MacroStep(BaseModel):
    op: str  # "write" | "read" | "pwm" | "blink"
    data: Dict[str, Any]

class GPIOMacroRequest(TargetedRequest):
    steps: List[MacroStep]
    mode: Optional[str] = None

def macro_run(req: GPIOMacroRequest) -> GPIOSimpleResponse:
    pol = _get_gpio_policy(req.target)
    if not pol:
        return GPIOSimpleResponse(ok=False, error=f"GPIO policy missing for target {req.target}")
    default_mode = pol.get("default_mode", "BCM").upper()
    mode = (req.mode or default_mode).upper()
    # Validate each step against pin allowlist and capability
    for st in req.steps:
        op = st.op
        d = st.data or {}
        pin = int(d.get("pin", -1))
        if pin < 0:
            return GPIOSimpleResponse(ok=False, error=f"invalid pin in step {st}")
        cap = "write" if op == "write" else ("read" if op == "read" else ("pwm" if op == "pwm" else ("write" if op == "blink" else None)))
        if not cap:
            return GPIOSimpleResponse(ok=False, error=f"unknown op {op}")
        _validate_pin(req.target, pin, d.get("mode") or mode, cap)

    payload = {
        "op": "macro",
        "data": {
            "steps": [s.model_dump() for s in req.steps]
        }
    }
    agent = pol.get("agent_path")
    if not agent:
        return GPIOSimpleResponse(ok=False, error="agent_path missing in policy")
    with use_client(req.target) as cli:
        r = cli.exec(f'python3 "{agent}" "{_b64(payload)}"')
        try:
            out = json.loads(r.stdout or "{}")
        except Exception:
            out = {"ok": False, "error": "invalid agent output", "raw": r.stdout}
        if out.get("ok"):
            return GPIOSimpleResponse(ok=True, result=out)
        return GPIOSimpleResponse(ok=False, error=out.get("error") or r.stderr)

TOOL_GPIO_MACRO_RUN = {
    "name": "macro_run",
    "description": "Run a validated sequence of GPIO ops: write/read/pwm.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "steps": {"type": "array", "items": {"type": "object"}},
            "mode": {"type": "string"}
        },
        "required": ["target", "steps"]
    },
    "output_schema": TOOL_GPIO_WRITE["output_schema"]
}
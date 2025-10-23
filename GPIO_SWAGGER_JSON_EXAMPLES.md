# GPIO Tools - Swagger UI JSON Examples

## 🔌 **Complete JSON Examples for Swagger UI Testing**

### **1. GPIO Write - Set Pin HIGH/LOW**

#### **Basic Write (Set Pin 17 HIGH)**
```json
{
  "target": "pi-lan",
  "pin": 17,
  "value": 1,
  "mode": "BCM",
  "direction": "out"
}
```

#### **Set Pin LOW**
```json
{
  "target": "pi-lan",
  "pin": 17,
  "value": 0,
  "mode": "BCM",
  "direction": "out"
}
```

#### **Set Pin HIGH (Boolean)**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "value": true,
  "mode": "BCM",
  "direction": "out"
}
```

#### **Set Pin LOW (Boolean)**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "value": false,
  "mode": "BCM",
  "direction": "out"
}
```

#### **Using BOARD Mode**
```json
{
  "target": "pi-lan",
  "pin": 11,
  "value": 1,
  "mode": "BOARD",
  "direction": "out"
}
```

---

### **2. GPIO Read - Read Pin State**

#### **Basic Read**
```json
{
  "target": "pi-lan",
  "pin": 17,
  "mode": "BCM",
  "direction": "in"
}
```

#### **Read with Pull-Up**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "mode": "BCM",
  "direction": "in",
  "pull": "up"
}
```

#### **Read with Pull-Down**
```json
{
  "target": "pi-lan",
  "pin": 22,
  "mode": "BCM",
  "direction": "in",
  "pull": "down"
}
```

#### **Read with No Pull**
```json
{
  "target": "pi-lan",
  "pin": 23,
  "mode": "BCM",
  "direction": "in",
  "pull": "off"
}
```

#### **Read Using BOARD Mode**
```json
{
  "target": "pi-lan",
  "pin": 11,
  "mode": "BOARD",
  "direction": "in"
}
```

---

### **3. GPIO PWM - Pulse Width Modulation**

#### **Basic PWM (50% Duty Cycle)**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "duty": 50.0,
  "freq": 1000.0,
  "duration": 2.0,
  "mode": "BCM"
}
```

#### **High Frequency PWM**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "duty": 75.0,
  "freq": 2000.0,
  "duration": 1.0,
  "mode": "BCM"
}
```

#### **Low Frequency PWM (Servo Control)**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "duty": 7.5,
  "freq": 50.0,
  "duration": 1.0,
  "mode": "BCM"
}
```

#### **Quick PWM Burst**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "duty": 25.0,
  "freq": 500.0,
  "duration": 0.5,
  "mode": "BCM"
}
```

#### **Continuous PWM (No Duration)**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "duty": 60.0,
  "freq": 1000.0,
  "duration": 0.0,
  "mode": "BCM"
}
```

---

### **4. GPIO Blink - LED Blinking**

#### **Basic Blink (5 times)**
```json
{
  "target": "pi-lan",
  "pin": 17,
  "mode": "BCM"
}
```

#### **Custom Blink Pattern**
```json
{
  "target": "pi-lan",
  "pin": 17,
  "count": 10,
  "on_time": 0.2,
  "off_time": 0.3,
  "mode": "BCM"
}
```

#### **Fast Blink**
```json
{
  "target": "pi-lan",
  "pin": 18,
  "count": 20,
  "on_time": 0.1,
  "off_time": 0.1,
  "mode": "BCM"
}
```

#### **Slow Blink**
```json
{
  "target": "pi-lan",
  "pin": 22,
  "count": 3,
  "on_time": 1.0,
  "off_time": 1.0,
  "mode": "BCM"
}
```

#### **Single Blink**
```json
{
  "target": "pi-lan",
  "pin": 23,
  "count": 1,
  "on_time": 0.5,
  "off_time": 0.0,
  "mode": "BCM"
}
```

#### **Rapid Blink Pattern**
```json
{
  "target": "pi-lan",
  "pin": 24,
  "count": 15,
  "on_time": 0.05,
  "off_time": 0.05,
  "mode": "BCM"
}
```

---

### **5. GPIO Macro Run - Complex Sequences**

#### **Simple Write Sequence**
```json
{
  "target": "pi-lan",
  "steps": [
    {
      "op": "write",
      "data": {
        "pin": 17,
        "value": 1,
        "mode": "BCM"
      }
    },
    {
      "op": "write",
      "data": {
        "pin": 18,
        "value": 0,
        "mode": "BCM"
      }
    }
  ],
  "mode": "BCM"
}
```

#### **Blink and PWM Sequence**
```json
{
  "target": "pi-lan",
  "steps": [
    {
      "op": "blink",
      "data": {
        "pin": 17,
        "count": 3,
        "on_time": 0.2,
        "off_time": 0.2,
        "mode": "BCM"
      }
    },
    {
      "op": "pwm",
      "data": {
        "pin": 18,
        "duty": 50.0,
        "freq": 1000.0,
        "duration": 2.0,
        "mode": "BCM"
      }
    },
    {
      "op": "write",
      "data": {
        "pin": 17,
        "value": 0,
        "mode": "BCM"
      }
    }
  ],
  "mode": "BCM"
}
```

#### **Sensor Reading and LED Response**
```json
{
  "target": "pi-lan",
  "steps": [
    {
      "op": "read",
      "data": {
        "pin": 22,
        "mode": "BCM",
        "direction": "in",
        "pull": "up"
      }
    },
    {
      "op": "write",
      "data": {
        "pin": 17,
        "value": 1,
        "mode": "BCM"
      }
    },
    {
      "op": "blink",
      "data": {
        "pin": 18,
        "count": 5,
        "on_time": 0.1,
        "off_time": 0.1,
        "mode": "BCM"
      }
    }
  ],
  "mode": "BCM"
}
```

#### **Complex Motor Control Sequence**
```json
{
  "target": "pi-lan",
  "steps": [
    {
      "op": "write",
      "data": {
        "pin": 17,
        "value": 1,
        "mode": "BCM"
      }
    },
    {
      "op": "pwm",
      "data": {
        "pin": 18,
        "duty": 25.0,
        "freq": 1000.0,
        "duration": 1.0,
        "mode": "BCM"
      }
    },
    {
      "op": "pwm",
      "data": {
        "pin": 18,
        "duty": 50.0,
        "freq": 1000.0,
        "duration": 1.0,
        "mode": "BCM"
      }
    },
    {
      "op": "pwm",
      "data": {
        "pin": 18,
        "duty": 75.0,
        "freq": 1000.0,
        "duration": 1.0,
        "mode": "BCM"
      }
    },
    {
      "op": "write",
      "data": {
        "pin": 17,
        "value": 0,
        "mode": "BCM"
      }
    }
  ],
  "mode": "BCM"
}
```

#### **SOS Pattern (3 short, 3 long, 3 short)**
```json
{
  "target": "pi-lan",
  "steps": [
    {
      "op": "blink",
      "data": {
        "pin": 17,
        "count": 3,
        "on_time": 0.1,
        "off_time": 0.1,
        "mode": "BCM"
      }
    },
    {
      "op": "blink",
      "data": {
        "pin": 17,
        "count": 3,
        "on_time": 0.3,
        "off_time": 0.1,
        "mode": "BCM"
      }
    },
    {
      "op": "blink",
      "data": {
        "pin": 17,
        "count": 3,
        "on_time": 0.1,
        "off_time": 0.1,
        "mode": "BCM"
      }
    }
  ],
  "mode": "BCM"
}
```

---

## 🎯 **Swagger UI Testing Tips**

### **1. Endpoint URLs**
- **GPIO Write**: `POST /tools/gpio/write`
- **GPIO Read**: `POST /tools/gpio/read`
- **GPIO PWM**: `POST /tools/gpio/pwm`
- **GPIO Blink**: `POST /tools/gpio/blink`
- **GPIO Macro**: `POST /tools/gpio/macro_run`

### **2. Common Parameters**
- **target**: Always use `"pi-lan"` (from your config)
- **pin**: Use pins 17, 18, 22, 23, 24, 25 (allowed in your config)
- **mode**: Use `"BCM"` or `"BOARD"` (BCM recommended)

### **3. Testing Order**
1. Start with **GPIO Write** to set pins
2. Use **GPIO Read** to verify states
3. Try **GPIO Blink** for LED effects
4. Test **GPIO PWM** for motor control
5. Use **GPIO Macro** for complex sequences

### **4. Expected Responses**
All tools return JSON with:
```json
{
  "ok": true/false,
  "result": {...},
  "error": "error message if any"
}
```

### **5. Error Handling**
- Invalid pins will return validation errors
- Missing target will return target not found
- SSH connection issues will return connection errors
- GPIO agent errors will return agent-specific errors

## 🚀 **Ready to Test!**

Copy any of these JSON examples into Swagger UI and test your GPIO functionality. All examples are ready to use with your current configuration!

---
type: "manual"
---

- make sure to only change what is necessary 
- use the GUI for config management vs the CLI, it's deprecated
- do not use SSH for any config management
- only document on release request
- make sure we support 
   - GS1920 ( 172.19.1.18 ) 
   - GS1915 ( 172.19.1.16 )
   - GS1900 ( 172.1.19.21 ) 
- generate a testing structure to validate different firmware versions for the different models as they're released
   - should be able to target an ip, with user and pass
- firmware version handling:
   - always detect model first using detect_model()
   - get firmware version using get_firmware_version() which caches result
   - use _compare_firmware_version() to check version compatibility
   - ensure all configuration methods check model before applying config
   - maintain backward compatibility across firmware versions (e.g., V1.15, V1.16)
- testing files by model:
   - test_all_config_18.py - GS1920 at 172.19.1.18
   - test_gs1915_16.py - GS1915 at 172.19.1.16
   - (create test for GS1900 at 172.1.19.21 when needed)
   
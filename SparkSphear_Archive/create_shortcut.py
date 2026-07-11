#!/usr/bin/env python3
"""
Create a Windows desktop shortcut for SparkSphear App
Run this once to create the shortcut
"""

import os
import sys

# Try to create Windows shortcut
try:
    import pythoncom
    from win32com.client import Dispatch
    
    # Paths
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    bat_file = os.path.join(desktop, "SparkSphear_App_Launcher.bat")
    shortcut_path = os.path.join(desktop, "SparkSphear Tech Workflow.lnk")
    
    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = bat_file
    shortcut.WorkingDirectory = desktop
    shortcut.Description = "SparkSphear Tech - Client Workflow & Diagnostics"
    shortcut.save()
    
    print(f"✅ Shortcut created: {shortcut_path}")
    print("\nYou can now double-click 'SparkSphear Tech Workflow' on your desktop!")
    
except ImportError:
    print("Note: win32com not installed.")
    print("To create a shortcut manually:")
    print("1. Right-click on 'SparkSphear_App_Launcher.bat'")
    print("2. Select 'Create shortcut'")
    print("3. Rename the shortcut to 'SparkSphear Tech Workflow'")
    print("4. Drag it to your desktop")
    
except Exception as e:
    print(f"Error creating shortcut: {e}")
    print("\nTo create a shortcut manually:")
    print("1. Right-click on 'SparkSphear_App_Launcher.bat'")
    print("2. Select 'Create shortcut'")
    print("3. Rename the shortcut to 'SparkSphear Tech Workflow'")
    print("4. Drag it to your desktop")

if __name__ == "__main__":
    print("Creating desktop shortcut for SparkSphear App...")
    print("=" * 60)
    
    # Try to create shortcut
    try:
        import pythoncom
        from win32com.client import Dispatch
        
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        bat_file = os.path.join(desktop, "SparkSphear_App_Launcher.bat")
        shortcut_path = os.path.join(desktop, "SparkSphear Tech Workflow.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = bat_file
        shortcut.WorkingDirectory = desktop
        shortcut.Description = "SparkSphear Tech - Client Workflow & Diagnostics"
        shortcut.save()
        
        print(f"✅ Shortcut created: {shortcut_path}")
        print("\nYou can now double-click 'SparkSphear Tech Workflow' on your desktop!")
        
    except ImportError:
        print("Note: win32com not installed.")
        print("\nTo create a shortcut manually:")
        print("1. Right-click on 'SparkSphear_App_Launcher.bat'")
        print("2. Select 'Create shortcut'")
        print("3. Rename the shortcut to 'SparkSphear Tech Workflow'")
        print("4. Drag it to your desktop")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo create a shortcut manually:")
        print("1. Right-click on 'SparkSphear_App_Launcher.bat'")
        print("2. Select 'Create shortcut'")
        print("3. Rename the shortcut to 'SparkSphear Tech Workflow'")
        print("4. Drag it to your desktop")

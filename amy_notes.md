You can remove the SD card from the RR robot and boot it on a Raspberry Pi. However, the company has changed the defaut username/password so you can't log into it directly.

You can insert an SD card with raspbian on it, install the RR code, and run it manually.
Revolution Robotics [publishes instructions](https://revolutionrobotics.org/pages/robot-framework-on-raspbian) on how to do this,
they are slightly incorrect. Here are the instructions with a few tweaks:

```
1. Download Raspbian and write it onto an SD card
2. Connect to wifi
3. Execute sudo raspi-config:

enable SSH
enable I2C
change Hostname if you want (it's easier to find your Raspberry on the network)
Force Audio to 3.5mm jack (if you don’t want to have sound from your HDMI monitor)
4. Update your Raspberry and run apt-get update, apt-get upgrade
5. Download and install our framework:

sudo apt-get install mpg123
cd ~
mkdir temp
cd temp
git clone https://github.com/RevolutionRobotics/RevvyLauncher.git
git clone https://github.com/RevolutionRobotics/RevvyFramework.git
cp -r RevvyLauncher/src/. "/home/pi/RevvyFramework"
cd RevvyFramework
python3 -m dev_tools.create_package
mkdir -p /home/pi/RevvyFramework/user/ble
mkdir -p /home/pi/RevvyFramework/user/data
cp install/framework.data "/home/pi/RevvyFramework/user/ble/2.data"
cp install/framework.meta "/home/pi/RevvyFramework/user/ble/2.meta"
cd ../..
rm -rf temp
cd RevvyFramework
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
python3 launch_revvy.py
6. Make sure that pip3 is working and it’s able to download packages. If you get errors after starting our framework that packages are missing (e.g. pybleno) pip3 couldn’t install the required packages.
```

I did this with the SD card in the freenova kit and everything worked but
the sounds - I have a feeling there may be a raspbian version issue there.

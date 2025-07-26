pkill -9 -f appium
pkill -9 -f node
devices=$(adb devices | grep -w "device" | cut -f1)
for device in $devices; do
  echo "Cleaning device: $device"
  adb -s $device uninstall io.appium.settings
  adb -s $device uninstall io.appium.uiautomator2.server
  adb -s $device uninstall io.appium.uiautomator2.server.test
done

echo "Starting appium ...."
appium
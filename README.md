# cumulocity-python-device-onboarding

This repo contains the following Python scripts compatible with Pyhton 2.7+:

c8y_onboard.py contains the Onboard Python class that can be used to quickly register a device in Cumulocity.
Credentials will be stored in a JSON file.

sensor.py can be used to simulate a sensor and generate any kind of measurement using a gaussian distribution to have a nice curve.

Finally simple_device.py simulates a device using both previous scripts and also handles firmware and software updates.

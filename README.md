# Google AdMob SDK for Cordova

This plugin is intended to be a dependency of other plugins.

## Dependents

* [cordova-plugin-admob-free](https://www.npmjs.com/package/cordova-plugin-admob-free)

## Disclaimer

This is NOT an official Google product. It is just a community-driven project,
repackaging SDKs for Cordova plugins.

## Installation

If you need to update the version of Play Services that is included by this
plugin you can edit your config.xml file:

```
<plugin name="cordova-admob-sdk" spec="../plugins/cordova-admob-sdk">
    <variable name="PLAY_SERVICES_VERSION" value="11.0.1" />
</plugin>

You just need to change the value to what your application needs. Note: This has been added for compatiblity with other plugins that include Play Services or FCM libraries.
```

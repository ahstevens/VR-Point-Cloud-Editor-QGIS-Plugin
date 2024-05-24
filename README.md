# Point Cloud Editor QGIS plugin
This is an experimental QGIS plugin to facilitate editing point clouds, which have been loaded into QGIS, using an external program.

## Development deployment

1. Edit [Makefile](point_cloud_editor/Makefile) setting `QGISDIR` to reflect the user profile where the plugin should
be installed.
2. Type `make deploy` each time you want to copy updated artifacts to the plugin directory under `QGISDIR`.
3. Enable the plugin in QGIS: Plugins > Installed > Point Cloud Editor
4. Enable the `Plugin Reloader` to reload the `Point Cloud Editor` plugin (each time you run `make deploy` you will 
need to reload the plugin. This avoids having to restart QGIS).
5. Run the plugin in QGIS: Plugins > Point Cloud Editor > Point Cloud Editor

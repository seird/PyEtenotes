echo "Creating executable"

try {C:/Python39/Scripts/pyinstaller pyetenotes.spec}
catch {pyinstaller pyetenotes.spec}

try {Remove-Item "dist/pyetenotes/d3dcompiler_47.dll"} catch {}
try {Remove-Item "dist/pyetenotes/opengl32sw.dll"} catch {}
try {Remove-Item "dist/pyetenotes/Qt5Quick.dll"} catch {}
try {Remove-Item "dist/pyetenotes/Qt5Qml.dll"} catch {}
try {Remove-Item "dist/pyetenotes/libGLESv2.dll"} catch {}
try {Remove-Item "dist/pyetenotes/Qt5Network.dll"} catch {}
try {Remove-Item "dist/pyetenotes/Qt5QmlModels.dll"} catch {}
try {Remove-Item "dist/pyetenotes/Qt5Svg.dll"} catch {}
try {Remove-Item "dist/pyetenotes/Qt5WebSockets.dll"} catch {}

echo "Creating installer"
iscc pyetenotes.iss

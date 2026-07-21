# mitm/ — Setup automation for rads-tracker capture

Cross-platform helper to point an Android/iOS device at a local mitmproxy and install the CA cert. Works on macOS and Windows (and Linux).

## Requisitos

- **Python 3** instalado en el host (Mac/Windows).
- **mitmproxy** instalado:
  - macOS: `brew install mitmproxy`
  - Windows: `choco install mitmproxy` o descarga desde https://mitmproxy.org/downloads
  - Linux: `pip install mitmproxy`
- **adb** en el PATH (sólo necesario si automatizas Android). Viene con Android Studio o Platform-Tools.
- Mac/PC y el device en la **misma red Wi-Fi**.

## Uso rápido

```bash
# macOS / Linux
./mitm/setup.sh info        # IP, puerto, estado
./mitm/setup.sh start       # arranca mitmweb en background
./mitm/setup.sh device      # configura proxy + CA en el device
./mitm/setup.sh test        # confirma que captura tráfico
./mitm/setup.sh stop        # detiene mitmweb
```

```cmd
REM Windows
mitm\setup.bat info
mitm\setup.bat start
mitm\setup.bat device
mitm\setup.bat test
mitm\setup.bat stop
```

## ¿Qué hace cada comando?

| Comando | Acción |
|---|---|
| `info`   | Imprime IP local del host, puerto del proxy (8080), web UI (8081), estado de mitmproxy, devices conectados |
| `start`  | Arranca `mitmweb --listen-port 8080 --web-port 8081` en background (logs en `~/.mitmproxy/mitmweb.log`) |
| `stop`   | Detiene el `mitmweb` lanzado por `start` |
| `device` | Detecta Android vía `adb` o iOS vía USB. Para Android: setea el proxy con `adb settings`, prueba si el CA ya es de confianza (TLS probe a `example.com`), si no lo es hace `adb push` del cert y abre Settings → Security guiando los toques finales. Para iOS imprime los pasos guiados. |
| `test`   | Cuenta flujos antes/después de 30s mientras el usuario navega, reporta si capturó tráfico y si vio eventos `rads-tracker` |

## Limitación importante (Android 7+)

Desde Android 7 las apps **solo confían en CAs de usuario** si su `network_security_config` lo permite. Si tu APK de Rappi de producción no lo permite, mitmproxy no podrá interceptar su HTTPS aunque el cert esté instalado.

Soluciones, en orden de viabilidad:

1. **APK de QA/debug** que confíe en user CAs (suele existir si Charles ya funciona — es lo más probable en tu caso).
2. **Device rooteado**: mover el cert a `/system/etc/security/cacerts/`.
3. **Emulador Android Studio** con `adb root` + script para mover el cert al store del sistema.
4. **Frida** con script de SSL pinning bypass.

## Tras `setup.py test` exitoso

Cuando veas:
```
OK   Captured N new flow(s) — proxy connection works
OK   Found N rads-tracker event(s) — ready to validate Ads events
```
…entonces el siguiente paso es el addon de captura + el Keyword de Katalon para asserts (próximo entregable).

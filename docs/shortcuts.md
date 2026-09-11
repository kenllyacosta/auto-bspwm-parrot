# Guía de atajos — Parrot y Kali con bspwm

Guía del teclado y los botones configurados por este repositorio. Disponible también como [HTML para abrir sin conexión](shortcuts.html). Está pensada para la sesión **bspwm sobre X11**, con sxhkd, Kitty y Polybar instalados por el proyecto.

## 1. Antes de empezar

- **Super** es normalmente la tecla Windows; en algunos teclados aparece como Meta. **Shift** es Mayús; **Return** es Enter; **Print** es Impr Pant.
- El signo **+** significa mantener las teclas pulsadas juntas. No hay que escribir el signo más.
- **Foco** significa la ventana que recibe el teclado. El ratón también puede cambiarlo al pasar sobre otra ventana.
- Los diez escritorios se llaman **I–X**. Los números de los atajos son los de la fila superior: **0 corresponde al escritorio X**.
- Los atajos globales los gestiona sxhkd. Los de Kitty solo funcionan cuando el terminal tiene el foco.
- Selecciona **bspwm** al iniciar sesión. Estas combinaciones no se instalan como atajos de KDE, Xfce o Wayland.

En VMware, haz clic dentro de la VM antes de probar. El sistema anfitrión puede interceptar combinaciones; comprueba su configuración de captura de teclado si una tecla funciona fuera del invitado.

## 2. Los imprescindibles

| Combinación | Acción | Ejemplo o detalle |
| --- | --- | --- |
| **Super + Enter** | Abrir Kitty | Inicia una ventana de terminal con Zsh. |
| **Super + D** | Abrir Rofi en modo run | Escribe el nombre de un comando, como `firefox`, y pulsa Enter. Escape cancela. |
| **Super + Shift + F** | Abrir Firefox | Requiere que el comando `firefox` exista en PATH. |
| **Super + Shift + B** | Abrir Burp Suite | Requiere `burpsuite`; el atajo no instala la aplicación. |
| **Super + Shift + L** | Bloquear la sesión | Usa i3lock con fondo oscuro. Escribe tu contraseña y pulsa Enter para desbloquear. |
| **Super + W** | Solicitar cierre de la ventana | La aplicación puede pedir guardar cambios. |
| **Super + Shift + W** | Forzar cierre del cliente X | Puede perder trabajo sin guardar; úsalo cuando el cierre normal no responda. |
| **Super + Escape** | Recargar atajos | Envía USR1 a sxhkd después de editar su configuración; no lo inicia si está detenido. |

## 3. Mover el foco y organizar ventanas

En las filas con **flecha**, elige ←, ↓, ↑ o →. La dirección es relativa a la distribución de las ventanas, no una letra que debas escribir.

| Combinación | Acción | Cuándo usarla |
| --- | --- | --- |
| **Super + flecha** | Enfocar la ventana en esa dirección | Cambiar del editor al terminal vecino. |
| **Super + Shift + flecha** | Intercambiar el nodo enfocado con el vecino | Reordenar ventanas dentro del mosaico. |
| **Super + C** | Enfocar la siguiente ventana visible del escritorio | Recorrer ventanas del escritorio actual. |
| **Super + Shift + C** | Enfocar la anterior | Recorrerlas en sentido inverso. |
| **Super + G** | Intercambiar con la ventana de mayor tamaño | Reorganizar el espacio de trabajo. |
| **Super + O** | Ir hacia atrás en el historial de foco | Volver a una ventana enfocada anteriormente. |
| **Super + I** | Ir hacia delante en el historial de foco | Deshacer el recorrido anterior cuando exista historial. |
| **Super + grave** | Enfocar el último nodo | `grave` es el símbolo de acento grave del teclado; su ubicación depende de la distribución. |

Un atajo direccional puede no producir cambios si no existe un vecino válido. El historial tampoco tiene destinos hasta haber cambiado el foco.

## 4. Escritorios I–X

| Combinación | Acción | Detalle |
| --- | --- | --- |
| **Super + 1…9** | Ir al escritorio I…IX | El número selecciona su índice. |
| **Super + 0** | Ir al escritorio X | Es el décimo, no un escritorio cero. |
| **Super + Shift + 1…9** | Enviar la ventana a I…IX | Mueve la ventana; el comando no solicita seguirla. |
| **Super + Shift + 0** | Enviar la ventana a X | Útil para apartar una tarea. |
| **Super + Tab** | Volver al último escritorio | Alterna con el escritorio visitado anteriormente. |
| **Super + [** | Escritorio anterior del monitor actual | En sxhkd se llama `bracketleft`. |
| **Super + ]** | Escritorio siguiente del monitor actual | En sxhkd se llama `bracketright`. |

**Ejemplo:** abre Kitty con Super + Enter, envíalo al escritorio II con Super + Shift + 2 y entra allí con Super + 2. Los selectores numéricos usan índices de bspwm; con varios monitores, revisa el orden real antes de asumir una numeración por monitor.

## 5. Tamaño y presentación

| Combinación | Acción | Resultado |
| --- | --- | --- |
| **Super + T** | Estado tiled | La ventana ocupa su celda del mosaico. |
| **Super + Shift + T** | Estado pseudo_tiled | Conserva un tamaño ajustable dentro del espacio reservado por el mosaico. |
| **Super + S** | Estado floating | La ventana queda flotante. |
| **Super + F** | Estado fullscreen | La ventana ocupa la pantalla completa. Vuelve al mosaico con Super + T. |
| **Super + M** | Alternar tiled/monocle del escritorio | En monocle se aprovecha el área del escritorio para la ventana enfocada. No es el mismo estado que fullscreen. |
| **Super + Ctrl + flecha** | Mover una ventana flotante | Desplazamiento de 20 píxeles por pulsación. Activa floating primero. |
| **Super + Alt + flecha** | Ajustar tamaño mediante el script del proyecto | Paso de 20 píxeles en floating y 100 en otros estados. Prueba el borde alternativo si el primero no se puede mover. |

El ajuste de tamaño depende del borde disponible y la distribución. No significa que todas las flechas siempre amplíen la ventana: desplazan el borde correspondiente. Los antiguos atajos con H/J/K/L están comentados y **no están activos**.

## 6. Preselección: decidir dónde abrir la siguiente ventana

La preselección indica cómo dividir el espacio para una próxima inserción. No mueve por sí sola la ventana actual.

| Combinación | Acción | Detalle |
| --- | --- | --- |
| **Super + Ctrl + Alt + flecha** | Preseleccionar dirección | Elige izquierda, abajo, arriba o derecha. |
| **Super + Ctrl + 1…9** | Fijar proporción de división | 1 significa 0,1; 5 significa 0,5; 9 significa 0,9. Es una proporción, no un número de escritorio. |
| **Super + Ctrl + Espacio** | Cancelar preselección del nodo | Quita la indicación de la ventana o grupo enfocado. |
| **Super + Ctrl + Alt + Espacio** | Cancelar preselecciones del escritorio | Aplica la cancelación a sus nodos. |

**Ejemplo:** enfoca una ventana, pulsa Super + Ctrl + Alt + →, fija 0,5 con Super + Ctrl + 5 y abre otra terminal con Super + Enter. Para cancelar antes de abrirla, usa Super + Ctrl + Espacio.

## 7. Funciones avanzadas: nodos y marcas

bspwm organiza las ventanas en un árbol binario. Un nodo puede representar una ventana o un grupo; los siguientes atajos son más útiles cuando ya dominas el movimiento entre ventanas.

| Combinación | Acción | Significado |
| --- | --- | --- |
| **Super + P** | Enfocar el padre | Sube al grupo que contiene el nodo actual. |
| **Super + B** | Enfocar el hermano | Selecciona el otro nodo de la misma división. |
| **Super + ,** | Enfocar el primer hijo | Usa la tecla `comma`. Requiere un nodo con hijos. |
| **Super + .** | Enfocar el segundo hijo | Usa la tecla `period`. |
| **Super + Ctrl + M** | Alternar marked | Marca el nodo para operaciones posteriores. |
| **Super + Ctrl + X** | Alternar locked | Evita el cierre mediante la orden de cierre de bspwm; no bloquea la pantalla. |
| **Super + Ctrl + Y** | Alternar sticky | Mantiene el nodo en el escritorio activo del monitor. |
| **Super + Ctrl + Z** | Alternar private | Cambia cómo se permiten inserciones automáticas en ese árbol; no cifra ni oculta datos. |
| **Super + Y** | Enviar el nodo marcado más reciente al preseleccionado más reciente | Necesita una marca y una preselección válidas. |

Las cuatro marcas son interruptores: repite la combinación para desactivarlas. Para bloquear realmente la sesión usa **Super + Shift + L**. Para detalles de los selectores consulta el [manual de bspwm](https://man.archlinux.org/man/bspwm.1).

## 8. Capturas de pantalla

| Combinación | Captura | Uso |
| --- | --- | --- |
| **Print** | Región seleccionada | Selecciona el área con el ratón; el script usa `scrot -s`. |
| **Ctrl + Print** | Pantalla completa | Ejecuta la captura normal de scrot. |
| **Alt + Print** | Ventana enfocada con borde | Enfoca antes la ventana que quieres capturar. |

Las capturas se guardan en **`~/ScreenShots/`**, carpeta que se crea automáticamente. El nombre contiene fecha y hora, por ejemplo `2026-09-11-10-30-00-screenshot.png`. Se muestra una notificación al terminar. No se configura copia automática al portapapeles.

Estas combinaciones se ejecutan al **soltar Print**: el prefijo `@` de sxhkd indica liberación de tecla. En algunos portátiles puede hacer falta Fn para generar Print. Usa el atajo una vez por segundo como máximo si quieres evitar nombres coincidentes.

## 9. Atajos propios de Kitty

Se aplican dentro del terminal. Una **ventana interna de Kitty** es un panel dentro de su ventana gráfica; no equivale a una ventana de bspwm.

| Combinación | Acción | Detalle |
| --- | --- | --- |
| **Ctrl + Shift + Enter** | Abrir otra ventana interna | Usa el directorio de trabajo actual cuando Kitty puede determinarlo. |
| **Ctrl + Shift + T** | Abrir otra pestaña | También usa el directorio actual. |
| **Ctrl + flecha** | Enfocar un panel vecino de Kitty | Depende de que haya un vecino en el diseño actual. |
| **Ctrl + Shift + Z** | Alternar el diseño stack | Muestra un panel ocupando el espacio y permite volver al diseño previo. |
| **F1** | Copiar selección al búfer interno a | Selecciona texto primero. |
| **F2** | Pegar desde el búfer a | Revisa lo pegado antes de ejecutar comandos. |
| **F3** | Copiar selección al búfer interno b | Segundo búfer independiente. |
| **F4** | Pegar desde el búfer b | No es el portapapeles del escritorio. |

F1–F4 y Ctrl + flechas quedan asignados a Kitty y pueden no llegar al programa que corre dentro. Otros atajos predeterminados dependen de la versión instalada; esta tabla cubre las asignaciones explícitas del repositorio. Consulta la [documentación de Kitty](https://sw.kovidgoyal.net/kitty/overview/) para ampliar.

## 10. Botones de Polybar

La barra adaptable es el diseño predeterminado. Los elementos visibles dependen del ancho del monitor y del hardware.

| Elemento | Acción o información | Observación |
| --- | --- | --- |
| Escritorios I–X | Identifican los escritorios y el activo | También puedes cambiarlos con los atajos numéricos. |
| Volumen | Clic derecho abre `pavucontrol` | Permite elegir dispositivos y ajustar niveles. |
| Power | Clic izquierdo abre el menú de sesión | Navega con flechas y confirma con Enter; Escape cancela. |
| Fecha y hora | Información | No hay un calendario asociado por el proyecto. |
| Red | Muestra la dirección detectada | Se añade desde 1100 píxeles de ancho. |
| VPN y objetivo | Indicadores adicionales | Se añaden desde 1500 píxeles; no son botones para conectar una VPN o ejecutar un escaneo. |
| Batería | Estado de carga | Aparece si se detecta una batería. |

El menú Power ofrece **Lock** (bloquear), **Sleep** (bloquear y suspender), **Logout** (salir de bspwm), **Restart** (reiniciar) y **Shutdown** (apagar). Guarda el trabajo antes de confirmar las tres últimas: el script no incorpora una segunda confirmación. Suspensión y apagado dependen de los permisos y servicios de la sesión.

El diseño opcional `classic` conserva barras separadas. Su lanzador abre Rofi en modo **drun**, que muestra aplicaciones con entrada de escritorio; Super + D usa **run**, para comandos. Por eso sus listas pueden ser diferentes.

## 11. Recargar, salir y recuperar el escritorio

| Combinación | Acción | Precaución |
| --- | --- | --- |
| **Super + Escape** | Recargar sxhkd | Úsalo para cambios en sus atajos. |
| **Super + Alt + R** | Reiniciar bspwm | Recarga el gestor; no reinicia Linux. El arranque del escritorio puede volver a ejecutarse. |
| **Super + Alt + Q** | Salir de bspwm | Termina la sesión del gestor; guarda tu trabajo antes. |

Si los atajos no responden, abre una terminal disponible y ejecuta estos diagnósticos **dentro de la sesión gráfica**:

```bash
printf 'Sesión: %s; DISPLAY: %s\n' "$XDG_SESSION_TYPE" "$DISPLAY"
pgrep -a -u "$(id -u)" -x sxhkd
bspc query -D --names
command -v kitty rofi scrot i3lock
```

Comprueba que la sesión sea X11 y que `bspc` encuentre el gestor. Si sxhkd no está activo, inícialo desde esa terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
mkdir -p "$HOME/.cache"
sxhkd > "$HOME/.cache/sxhkd-manual.log" 2>&1 &
```

Si ya está activo, usa `pkill -USR1 -x sxhkd` para recargarlo. No ejecutes varias instancias. Si la barra no responde, reiníciala con:

```bash
bash "$HOME/.config/polybar/launch.sh"
```

Si conservas rutas antiguas o permisos incorrectos, ejecuta **desde la carpeta del repositorio**:

```bash
bash scripts/apply-config.sh
```

Este comando respalda la configuración actual y la reemplaza por la del proyecto. Incluye bspwm, sxhkd, Polybar, Picom, Kitty, Rofi y archivos de Zsh; conserva aparte tus personalizaciones. Después cierra sesión y selecciona bspwm. No sustituye la instalación de paquetes que falten.

Si no puedes abrir ninguna terminal gráfica, prueba una consola virtual con Ctrl + Alt + F3. Puede ser necesario enviar la combinación desde el hipervisor. La consola sirve para reparar archivos; arrancar sxhkd allí sin el entorno gráfico correcto no recupera los atajos por sí solo.

## 12. Personalizar y mantener esta guía

| Configuración del repositorio | Destino instalado | Qué controla |
| --- | --- | --- |
| [Config/sxhkd/sxhkdrc](../Config/sxhkd/sxhkdrc) | `~/.config/sxhkd/sxhkdrc` | Atajos globales. |
| [Config/kitty/kitty.conf](../Config/kitty/kitty.conf) | `~/.config/kitty/kitty.conf` | Atajos internos del terminal. |
| [Config/bspwm/bspwmrc](../Config/bspwm/bspwmrc) | `~/.config/bspwm/bspwmrc` | Arranque y reglas del gestor. |
| [Script de tamaño](../Config/bspwm/scripts/bspwm_resize) | `~/.config/bspwm/scripts/bspwm_resize` | Paso y dirección de ajuste. |
| [Script de capturas](../scripts/screenshot) | `~/.local/bin/screenshot` | Capturas y carpeta de destino. |
| [Barra adaptable](../Config/polybar/responsive.ini) | `~/.config/polybar/responsive.ini` | Módulos y botones. |
| [Menú Power](../Config/polybar/scripts/powermenu_alt) | `~/.config/polybar/scripts/powermenu_alt` | Acciones de sesión. |

En sxhkd, una línea sin sangría declara la combinación y la siguiente, con sangría, el comando. Las llaves agrupan alternativas correspondientes: `super + {t,s}` y `bspc node -t {tiled,floating}` representan dos atajos. Las líneas que empiezan con `#` son comentarios.

**Teclado español:** corchetes, coma, punto y acento grave dependen de los símbolos que genere tu distribución. Si una combinación no sale con facilidad, cámbiala por otra libre en sxhkd y recarga. No asumas que la posición física de un teclado estadounidense coincide con la tuya.

La guía no fija atajos de NvChad: el instalador descarga su configuración actual y pueden variar entre versiones. Para el gestor y el terminal, actualiza este Markdown cuando cambies sus asignaciones y regenera el HTML con:

```bash
python3 scripts/build_shortcuts.py
```

La generación usa solo la biblioteca estándar de Python. El HTML contiene sus estilos, permite imprimir y se abre sin conexión; no carga fuentes, scripts ni servicios externos. Los enlaces a archivos del proyecto necesitan conservar la estructura del repositorio.

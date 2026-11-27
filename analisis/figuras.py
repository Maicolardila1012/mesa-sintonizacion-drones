"""
Genera las figuras del documento (../figuras/*.png) a partir de calculos_mecanicos.py
y las láminas fotográficas a partir de ../fotos/.
Ejecutar:  python3 figuras.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Arc
from PIL import Image, ImageDraw, ImageFont, ImageOps

import calculos_mecanicos as cm

AQUI = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(AQUI, "..", "imagenes", "resultados")
FOTOS = os.path.join(AQUI, "..", "imagenes", "implementacion")
os.makedirs(FIG, exist_ok=True)

AZUL = "#257de0"
AZUL_CLARO = "#84b9f3"
AZUL_OSC = "#1757ac"
GRIS = "#9a9a9a"
GRIS_OSC = "#4d4d4d"
TXT = "#191919"
TXT2 = "#666666"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#bdbdbd",
    "axes.labelcolor": TXT, "xtick.color": TXT2, "ytick.color": TXT2,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200,
})


def titulo(ax, t, sub=None):
    ax.set_title(t, loc="left", fontsize=12, color=TXT, pad=18 if sub else 8, fontweight="bold")
    if sub:
        ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=9, color=TXT2, va="bottom")


# ---------------------------------------------------------------- Fig. 1 esquema cinemático 3D
def fig_esquema():
    fig = plt.figure(figsize=(7.5, 7))
    ax = fig.add_subplot(111, projection="3d")
    t = np.linspace(0, 2 * np.pi, 200)
    # U en plano XZ (semicírculo inferior)
    tu = np.linspace(np.pi, 2 * np.pi, 100)
    ax.plot(cm.R_U * np.cos(tu), 0 * tu, cm.R_U * np.sin(tu), color=GRIS_OSC, lw=3, label="Soporte en U Ø1,50 m")
    ax.plot([0, 0], [0, 0], [-cm.R_U, -cm.R_U - 0.18], color=GRIS_OSC, lw=4)
    # brazos de la U hasta el aro exterior
    for s in (-1, 1):
        ax.plot([s * cm.R_U, s * cm.R_EXT], [0, 0], [0, 0], color=GRIS_OSC, lw=3)
    # aro exterior horizontal XY
    ax.plot(cm.R_EXT * np.cos(t), cm.R_EXT * np.sin(t), 0 * t, color=AZUL_OSC, lw=2.5, label="Aro exterior Ø1,20 m")
    for s in (-1, 1):
        ax.plot([0, 0], [s * cm.R_EXT, s * cm.R_INT], [0, 0], color=AZUL_OSC, lw=2.5)
    # aro interior vertical YZ
    ax.plot(0 * t, cm.R_INT * np.cos(t), cm.R_INT * np.sin(t), color=AZUL, lw=2.5, label="Aro interior Ø1,00 m")
    # guía vertical
    ax.plot([0, 0], [0, 0], [-cm.R_INT, 0], color="#f2a600", lw=4, label="Guía vertical (carrera 20 cm)")
    ax.plot([0, 0], [0, 0], [0, cm.CARRERA], color="#f2a600", lw=2, ls="--")
    ax.scatter([0], [0], [0], s=60, color=TXT, zorder=5)
    # ejes de giro
    def eje(p0, p1, c, txt):
        ax.plot(*zip(p0, p1), color=c, lw=1, ls=(0, (4, 3)))
        ax.text(*p1, txt, color=c, fontsize=10, fontweight="bold")
    eje((-0.95, 0, 0), (0.95, 0, 0), TXT, "X  alabeo")
    eje((0, -0.85, 0), (0, 0.85, 0), TXT, "Y  cabeceo")
    eje((0, 0, -0.98), (0, 0, 0.75), TXT, "Z  guiñada")
    ax.text(0.0, 0.0, cm.CARRERA + 0.09, "dron", fontsize=9, color=TXT2, ha="center")
    fig.text(0.62, 0.12, "X: chumaceras de pie 7/8\"\nY: rodamientos 6004 (muñón 20 mm)\nZ: chumacera plana 7/8\"\nGuía: 50 → 70 cm", fontsize=9, color=TXT, va="bottom")
    ax.set_box_aspect((1, 1, 1))
    lim = 0.85
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim - 0.15, lim - 0.15)
    ax.view_init(elev=18, azim=-58)
    ax.set_axis_off()
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    fig.suptitle("Arquitectura cinemática: cardán de 3 ejes + guía vertical (4 GDL)",
                 x=0.04, ha="left", fontsize=12, fontweight="bold", color=TXT)
    fig.savefig(os.path.join(FIG, "fig01_esquema_cinematico.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig. 2 vista frontal acotada
def fig_cotas():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 5.6), gridspec_kw={"width_ratios": [1.25, 1]})
    t = np.linspace(0, 2 * np.pi, 300)
    tu = np.linspace(np.pi, 2 * np.pi, 100)

    def cota_h(ax, y, x0, x1, txt):
        ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=TXT2, lw=0.9))
        ax.text((x0 + x1) / 2, y + 0.03, txt, ha="center", fontsize=9.5, color=TXT)

    def cota_v(ax, x, y0, y1, txt, ha="left"):
        ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=TXT2, lw=0.9))
        ax.text(x + (0.03 if ha == "left" else -0.03), (y0 + y1) / 2, txt, ha=ha, va="center", fontsize=9.5, color=TXT)

    # (a) vista frontal: plano de la U
    ax = a1
    ax.plot(cm.R_U * np.cos(tu), cm.R_U * np.sin(tu), color=GRIS_OSC, lw=3)
    ax.plot([0, 0], [-cm.R_U, -cm.R_U - 0.12], color=GRIS_OSC, lw=4)
    ax.plot([-0.4, 0.4], [-cm.R_U - 0.12] * 2, color=GRIS_OSC, lw=4)
    for sg in (-1, 1):
        ax.plot([sg * cm.R_U, sg * cm.R_EXT], [0, 0], color=GRIS_OSC, lw=3)
        ax.plot(sg * cm.R_U, 0, "o", color=TXT, ms=6)
    ax.plot([-cm.R_EXT, cm.R_EXT], [0, 0], color=AZUL_OSC, lw=3)
    ax.plot([0, 0], [-cm.R_INT, cm.R_INT], color=AZUL, lw=3)
    ax.plot(0, -cm.R_U - 0.12, "s", color=TXT, ms=7)
    cota_h(ax, 0.56, -cm.R_U, cm.R_U, "Soporte en U  Ø 1,50 m")
    cota_h(ax, 0.05, -cm.R_EXT, cm.R_EXT, "Aro exterior  Ø 1,20 m")
    ax.text(cm.R_U + 0.03, -0.09, "chumacera\nde pie (X)", fontsize=8.5, color=TXT2)
    ax.text(0.04, -cm.R_U - 0.16, "chumacera plana (Z)", fontsize=8.5, color=TXT2, va="top")
    ax.text(0.04, cm.R_INT - 0.18, "aro interior\n(de canto)", fontsize=8.5, color=TXT2)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-0.95, 1.05); ax.set_ylim(-1.0, 0.68)
    ax.set_title("(a) Vista frontal: U y aro exterior", loc="left", fontsize=10.5, color=TXT)

    # (b) vista lateral: aro interior y guía vertical
    ax = a2
    ax.plot(cm.R_INT * np.cos(t), cm.R_INT * np.sin(t), color=AZUL, lw=3)
    ax.plot([-cm.R_EXT, cm.R_EXT], [0, 0], color=AZUL_OSC, lw=3, alpha=0.35)
    for sg in (-1, 1):
        ax.plot(sg * cm.R_INT, 0, "o", color=TXT, ms=6)
    ax.plot([0, 0], [-cm.R_INT, 0], color="#f2a600", lw=5)
    ax.plot([0, 0], [0, cm.CARRERA], color="#f2a600", lw=2.5, ls="--")
    for yy in (0, cm.CARRERA):
        ax.plot([-0.1, 0.1], [yy, yy], color=TXT, lw=2.5)
    cota_h(ax, 0.6, -cm.R_INT, cm.R_INT, "Aro interior  Ø 1,00 m")
    cota_v(ax, 0.16, -cm.R_INT, 0, "50 cm: posición inicial\n(dron en el centro)")
    cota_v(ax, 0.16, 0, cm.CARRERA, "+20 cm (tope 70 cm)")
    ax.text(cm.R_INT + 0.03, -0.09, "balinera (Y)", fontsize=8.5, color=TXT2)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-0.65, 0.95); ax.set_ylim(-0.95, 0.75)
    ax.set_title("(b) Vista lateral: aro interior y guía", loc="left", fontsize=10.5, color=TXT)
    fig.suptitle("Dimensiones principales de la mesa", x=0.02, ha="left", fontsize=12, fontweight="bold", color=TXT)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(FIG, "fig02_dimensiones.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig. 3 inercias
def fig_inercias():
    ejes = list(cm.inercia.keys())
    comps = ["Aro interior", "Guía vertical", "Aro exterior", "Semicírculo U", "Ejes"]
    colores = {"Aro interior": AZUL, "Guía vertical": AZUL_CLARO, "Aro exterior": GRIS_OSC, "Semicírculo U": GRIS, "Ejes": "#cfcfcf"}
    r = [sum(cm.inercia[e].values()) / (cm.I_dron_z if "Z" in e else cm.I_dron_xy) for e in ejes]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    y = np.arange(len(ejes))[::-1]
    for i, e in enumerate(ejes):
        left = 0
        for c in comps:
            v = cm.inercia[e].get(c, 0)
            if v:
                ax.barh(y[i], v, left=left, color=colores[c], height=0.5, edgecolor="white", linewidth=2,
                        label=c if (i == 1 and c != "Semicírculo U") or (i == 2 and c == "Semicírculo U") else None)
                left += v
        Iref = cm.I_dron_z if "Z" in e else cm.I_dron_xy
        ax.text(left + 0.03, y[i], f"{left:.2f} kg·m²  (≈{left / Iref:.0f}× el dron)".replace(".", ","), va="center", fontsize=9.5, color=TXT)
    ax.set_yticks(y, ejes)
    ax.set_xlabel("Momento de inercia del cardán (kg·m²)")
    ax.set_xlim(0, 3.0)
    ax.grid(axis="x", color="#ececec"); ax.set_axisbelow(True)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h, l, frameon=False, ncol=5, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.45, -0.18))
    titulo(ax, f"El cardán aporta entre {min(r):.0f} y {max(r):.0f} veces la inercia del dron",
           f"Inercia calculada por eje; dron de referencia clase 450 mm, 2 kg (Ixx≈{cm.I_dron_xy:.3f}; Izz≈{cm.I_dron_z:.3f} kg·m²)".replace(".", ","))
    fig.savefig(os.path.join(FIG, "fig03_inercias_por_eje.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig. 4 par gravitacional
def fig_par():
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    th = np.linspace(0, np.pi / 2, 100)
    estilos = [(0.0, AZUL_CLARO, "dron en el centro (50 cm)"), (0.10, AZUL, "+10 cm (60 cm)"),
               (0.20, AZUL_OSC, "+20 cm (70 cm, tope)")]
    for h, c, lab in estilos:
        tau = cm.par_grav(th, h)
        ax.plot(np.degrees(th), tau, color=c, lw=2)
        ax.text(91, tau[-1], lab, va="center", fontsize=9, color=TXT)
    ax.axhline(0, color="#bdbdbd", lw=1)
    ax.text(48, 1.55, "zona desestabilizante\n(péndulo invertido)", fontsize=8.5, color=TXT2)
    ax.text(48, -0.55, "zona restauradora (péndulo)", fontsize=8.5, color=TXT2)
    ax.set_xlim(0, 90); ax.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax.set_xlabel("Inclinación en cabeceo o alabeo (°)")
    ax.set_ylabel("Par gravitacional (N·m)")
    ax.grid(axis="y", color="#ececec")
    hn = (cm.M_POSTE * cm.g * cm.L_POSTE / 2) / (cm.M_DRON * cm.g + cm.M_POSTE * cm.g / 2)
    titulo(ax, f"Por encima de {hn * 100:.1f} cm sobre el centro el sistema se vuelve inestable".replace(".", ","),
           "Par por desbalance de masa respecto al centro del cardán (dron 2 kg, guía 0,6 kg)")
    fig.savefig(os.path.join(FIG, "fig05_par_gravitacional.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig. 5 deformadas FEM
def fig_fem():
    caso = "Reposo (dron apoyado, sin empuje)"
    d_i, d_e, xy_i, u_i, xy_e, u_e = cm.res_fem[caso]
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.4))
    esc_i = 0.08 / max(abs(u_i[1::3]).max(), 1e-9)
    ax = axs[0]
    c = np.r_[xy_i, xy_i[:1]]
    def_ = np.c_[xy_i[:, 0] + esc_i * u_i[0::3], xy_i[:, 1] + esc_i * u_i[1::3]]
    def_ = np.r_[def_, def_[:1]]
    ax.plot(c[:, 0], c[:, 1], color=GRIS, lw=1.2, ls="--")
    ax.plot(def_[:, 0], def_[:, 1], color=AZUL, lw=2.2)
    ax.plot([-cm.R_INT, cm.R_INT], [0, 0], "^", color=TXT, ms=9)
    ax.annotate("", (0, -cm.R_INT - 0.02), (0, -cm.R_INT - 0.22), arrowprops=dict(arrowstyle="<-", color=TXT, lw=1.4))
    ax.text(0.03, -cm.R_INT - 0.2, "dron + guía\n25,5 N", fontsize=8.5, color=TXT)
    ax.text(0, 0.08, f"δ fondo = {abs(d_i) * 1e3:.2f} mm".replace(".", ","), ha="center", fontsize=10, color=TXT, fontweight="bold")
    ax.set_title("Aro interior (en su plano)", fontsize=10.5, color=TXT, loc="left")
    ax.set_aspect("equal"); ax.axis("off")

    ax = axs[1]
    w = u_e[0::3]
    th = np.linspace(0, 2 * np.pi, len(w), endpoint=False)
    ax.plot(np.degrees(th), w * 1e3, color=AZUL, lw=2.2)
    ax.axhline(0, color="#bdbdbd", lw=1)
    for a in (0, 180):
        ax.plot(a, 0, "^", color=TXT, ms=9)
    ax.set_xticks([0, 90, 180, 270, 360], ["0°\napoyo U", "90°\npivote int.", "180°\napoyo U", "270°\npivote int.", "360°"])
    ax.set_ylabel("Desplazamiento vertical (mm)")
    ax.text(90, w.min() * 1e3 * 1.08, f"{abs(w.min()) * 1e3:.1f} mm".replace(".", ","), ha="center", va="top", fontsize=10,
            color=TXT, fontweight="bold")
    ax.set_ylim(w.min() * 1e3 * 1.35, 0.4)
    ax.set_title("Aro exterior (fuera de su plano)", fontsize=10.5, color=TXT, loc="left")
    ax.grid(axis="y", color="#ececec")
    fig.suptitle(f"Rigidez: la flecha máxima es {abs(w.min()) * 1e3:.1f} mm, en el aro exterior".replace(".", ","), x=0.02, ha="left",
                 fontsize=12, fontweight="bold", color=TXT)
    fig.text(0.02, 0.9, "Modelo de vigas (tubo 1/2\" cal. 16, E = 200 GPa), caso en reposo con dron de 2 kg; deformada izquierda exagerada",
             fontsize=8.5, color=TXT2)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(os.path.join(FIG, "fig04_rigidez_aros_fem.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Láminas fotográficas
def lamina(archivos, etiquetas, salida, titulo_txt, cols):
    W, H = 600, 800
    filas = int(np.ceil(len(archivos) / cols))
    pad, top, cap = 16, 60, 56
    lienzo = Image.new("RGB", (cols * W + (cols + 1) * pad, top + filas * (H + cap + pad) + pad), "white")
    d = ImageDraw.Draw(lienzo)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        f_c = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
        f_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except OSError:
        f_t = f_c = f_l = ImageFont.load_default()
    d.text((pad, 18), titulo_txt, fill=TXT, font=f_t)
    for k, (a, e) in enumerate(zip(archivos, etiquetas)):
        r, c = divmod(k, cols)
        im = ImageOps.fit(Image.open(os.path.join(FOTOS, a)).convert("RGB"), (W, H))
        x = pad + c * (W + pad); y = top + r * (H + cap + pad)
        lienzo.paste(im, (x, y))
        letra = "(" + "abcdefgh"[k] + ")"
        d.rectangle([x + 8, y + 8, x + 58, y + 42], fill="white")
        d.text((x + 14, y + 11), letra, fill=TXT, font=f_l)
        for i, linea in enumerate(e.split("\n")):
            d.text((x, y + H + 6 + i * 24), linea, fill=TXT, font=f_c)
    lienzo.save(os.path.join(FIG, salida), quality=88)


if __name__ == "__main__":
    fig_esquema(); fig_cotas(); fig_inercias(); fig_par(); fig_fem()
    lamina(["foto03_guinada_vista_superior.jpg", "foto02_guinada_chumacera_plana.jpg",
            "foto01_alabeo_chumacera_pie.jpg", "foto05_alabeo_chumacera_pie_capuchon.jpg",
            "foto06_cabeceo_balinera_placa_freno.jpg", "foto08_union_soldada_eje_aro.jpg"],
           ["Guiñada: soporte tipo freno 5 mm\n(4 agujeros 3/8\") sobre la chumacera plana",
            "Guiñada: chumacera plana 7/8\"\nsoldada a la base",
            "Alabeo: chumacera de pie 7/8\"\nen canal de acero",
            "Alabeo: chumacera de pie, placa\nde freno y capuchón PETG",
            "Cabeceo: rodamiento 6004 en placa\nde freno; muñón rebajado a 20 mm",
            "Unión soldada eje 7/8\" – aro\n(tubo 1/2\" cal. 16)"],
           "lamina01_articulaciones.jpg", "Lámina 1. Articulaciones del cardán (implementación)", cols=3)
    lamina(["foto04_sistema_vuelo_vertical.jpg", "foto07_guia_telescopica_detalle.jpg"],
           ["Guía vertical con soporte del\ndron impreso en PETG",
            "Detalle de la guía telescópica\ny arandelas de tope soldadas"],
           "lamina02_sistema_vuelo.jpg", "Lámina 2. Sistema de vuelo vertical", cols=2)
    print("figuras listas:", sorted(os.listdir(FIG)))

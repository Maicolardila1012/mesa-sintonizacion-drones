"""
Cálculos mecánicos de la mesa de sintonización para drones (cardán de 3 ejes + guía vertical).

Ejecutar:  python3 calculos_mecanicos.py
Salidas:   ../datos/*.csv  y  resultados impresos en consola.

Todas las hipótesis están en la sección PARAMETROS. Los valores marcados (*) son
supuestos o nominales y deben confirmarse con medición.
"""
import csv
import math
import os
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "..", "datos")
os.makedirs(DATOS, exist_ok=True)

# ----------------------------------------------------------------------------- PARAMETROS
g = 9.81
RHO = 7850.0            # kg/m3 acero
E = 200e9               # Pa
G = 79e9                # Pa
SY_EJE = 210e6          # Pa, acero AISI/SAE 1020 (grado confirmado por el autor); Sy de laminado en caliente (conservador)

# Tubo galvanizado 1/2" calibre 16: Ø ext. 21,3 mm (1/2" NPS) y espesor calibre 16 ≈ 1,5 mm (1,52 mm)
# Masa lineal con la fórmula de tubo estructural redondo: P = 0,0246615·e·(D − e) kg/m
D_TUBO = 21.3e-3
T_TUBO = 1.5e-3
d_int = D_TUBO - 2 * T_TUBO
A_TUBO = math.pi / 4 * (D_TUBO**2 - d_int**2)
I_TUBO = math.pi / 64 * (D_TUBO**4 - d_int**4)
J_TUBO = 2 * I_TUBO
ML_TUBO = RHO * A_TUBO  # kg/m

D_EJE = 7 / 8 * 25.4e-3   # 22.225 mm
D_MUNON = 20e-3           # muñón rebajado para las balineras del aro interior

R_U = 1.50 / 2            # semicírculo en U, Ø 1,50 m (diámetro, confirmado)
R_EXT = 1.20 / 2
R_INT = 1.00 / 2

M_POSTE = 0.60            # kg, guía vertical + soporte PETG (*) valor asumido, por pesar

# Ejes macizos de 7/8" (confirmados por el autor salvo los muñones, deducidos de la geometría)
L_EJE_U = 0.18            # eje vertical que sostiene la U (guiñada)
L_EJE_LAT = 0.15          # cada brazo recto entre la chumacera de pie y la U (= R_U - R_EXT)
L_MUNON = R_EXT - R_INT   # 0,10 m, cada muñón entre aro interior y rodamiento 6004
L_POSTE = 0.50            # m, de la base del aro interior al soporte del dron (posición inicial)
CARRERA = 0.20            # m, 50 -> 70 cm

# Caso de diseño (*): dron de 2,0 kg con relación empuje/peso 2:1
M_DRON = 2.0
T_MAX = 2.0 * M_DRON * g

# Dron de referencia para comparar inercias (*): cuadricóptero clase 450 mm
M_MOTOR = 0.08            # motor + hélice
R_BRAZO = 0.225
M_CUERPO = 1.0 * M_DRON - 4 * M_MOTOR  # resto concentrado como placa
# -----------------------------------------------------------------------------


def guardar(nombre, filas, encabezado):
    with open(os.path.join(DATOS, nombre), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)


# 1. Masas ---------------------------------------------------------------------
L_U = math.pi * R_U
L_EXT = 2 * math.pi * R_EXT
L_INT = 2 * math.pi * R_INT
m_U = ML_TUBO * L_U
m_ext = ML_TUBO * L_EXT
m_int = ML_TUBO * L_INT

ML_EJE = RHO * math.pi / 4 * D_EJE**2   # 3,05 kg/m (catálogo Ternium: 3,042 kg/m)
m_eje_U = ML_EJE * L_EJE_U
m_eje_lat = ML_EJE * L_EJE_LAT
m_munon = ML_EJE * L_MUNON               # se toma la barra de 7/8" completa (conservador)

masas = [
    ("Semicírculo en U (Ø1,50 m)", L_U, m_U),
    ("Aro exterior (Ø1,20 m)", L_EXT, m_ext),
    ("Aro interior (Ø1,00 m)", L_INT, m_int),
    ("Eje vertical de la U (7/8\")", L_EJE_U, m_eje_U),
    ("Brazos laterales 7/8\" (2 × 15 cm)", 2 * L_EJE_LAT, 2 * m_eje_lat),
    ("Muñones del aro interior (2 × 10 cm)", 2 * L_MUNON, 2 * m_munon),
]
guardar("masas_calculadas.csv",
        [(n, f"{L:.3f}", f"{m:.2f}") for n, L, m in masas] +
        [("Guía vertical + soporte (valor asumido)", f"{L_POSTE:.3f}", f"{M_POSTE:.2f}")],
        ["componente", "longitud_m", "masa_kg"])

# 2. Inercias por eje ----------------------------------------------------------
# Ejes: Z = guiñada (vertical, chumacera plana), X = alabeo (aro exterior, chumaceras de pie),
#       Y = cabeceo (aro interior, balineras).
# Reposo: U en plano XZ, aro exterior horizontal (XY), aro interior vertical (YZ),
#         poste sobre Z desde -R_INT hasta 0.
I_poste = M_POSTE * L_POSTE**2 / 3          # barra desde el centro hacia abajo, respecto a eje horizontal por el centro
def I_barra_radial(m, r1, r2):
    """Barra a lo largo de un radio, de r1 a r2, respecto a un eje perpendicular por el centro."""
    return m * (r1**2 + r1 * r2 + r2**2) / 3

I_munones = 2 * I_barra_radial(m_munon, R_INT, R_EXT)
I_laterales = 2 * I_barra_radial(m_eje_lat, R_EXT, R_U)
inercia = {
    "Cabeceo (Y)": {"Aro interior": 0.5 * m_int * R_INT**2, "Guía vertical": I_poste},
    "Alabeo (X)": {"Aro exterior": 0.5 * m_ext * R_EXT**2, "Aro interior": m_int * R_INT**2,
                   "Guía vertical": I_poste, "Ejes": I_munones},
    "Guiñada (Z)": {"Semicírculo U": 0.5 * m_U * R_U**2, "Aro exterior": m_ext * R_EXT**2,
                    "Aro interior": 0.5 * m_int * R_INT**2, "Ejes": I_munones + I_laterales},
}
filas = []
for eje, comp in inercia.items():
    for c, v in comp.items():
        filas.append((eje, c, f"{v:.4f}"))
guardar("inercias_por_eje.csv", filas, ["eje", "componente", "inercia_kg_m2"])

# Dron de referencia (masas puntuales en configuración X + cuerpo como placa 0,15 x 0,15 m)
a = R_BRAZO * math.sqrt(0.5)
I_dron_xy = 4 * M_MOTOR * a**2 + M_CUERPO * (0.15**2) / 12
I_dron_z = 4 * M_MOTOR * R_BRAZO**2 + M_CUERPO * (0.15**2 + 0.15**2) / 12

# 3. Par gravitacional vs altura del dron -------------------------------------
def par_grav(theta, h):
    """Par (N·m) respecto al centro del cardán; h = altura del dron sobre el centro.
    Positivo = desestabilizante. El poste (masa bajo el centro) es restaurador."""
    z_poste = -L_POSTE / 2 + h / 2  # el tramo superior sube con el dron (aprox.)
    return (M_DRON * g * h + M_POSTE * g * z_poste) * np.sin(theta)

ang = np.radians(np.arange(0, 91, 5))
filas = []
for h in (0.0, 0.10, 0.20):
    for t in ang:
        filas.append((f"{h:.2f}", f"{math.degrees(t):.0f}", f"{par_grav(t, h):.3f}"))
guardar("par_gravitacional.csv", filas, ["h_sobre_centro_m", "angulo_deg", "par_Nm"])

# 4. FEM de los aros -----------------------------------------------------------
def fem_aro_en_plano(R, P_fondo, n=144):
    """Aro en su plano (pórtico 2D), apoyos articulados en los extremos del diámetro horizontal,
    carga puntual vertical en el punto inferior + peso propio. Devuelve desplazamiento vertical
    del punto inferior (m), momento máximo (N·m)."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    xy = np.c_[R * np.cos(th), R * np.sin(th)]
    ndof = 3 * n
    K = np.zeros((ndof, ndof)); F = np.zeros(ndof)
    elems = [(i, (i + 1) % n) for i in range(n)]
    q = ML_TUBO * g
    for i, j in elems:
        dx, dy = xy[j] - xy[i]; L = math.hypot(dx, dy); c, s = dx / L, dy / L
        EA, EI = E * A_TUBO, E * I_TUBO
        k = np.array([[EA/L,0,0,-EA/L,0,0],[0,12*EI/L**3,6*EI/L**2,0,-12*EI/L**3,6*EI/L**2],
                      [0,6*EI/L**2,4*EI/L,0,-6*EI/L**2,2*EI/L],[-EA/L,0,0,EA/L,0,0],
                      [0,-12*EI/L**3,-6*EI/L**2,0,12*EI/L**3,-6*EI/L**2],[0,6*EI/L**2,2*EI/L,0,-6*EI/L**2,4*EI/L]])
        T = np.zeros((6, 6)); r = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]]); T[:3,:3] = r; T[3:,3:] = r
        kg = T.T @ k @ T
        idx = [3*i, 3*i+1, 3*i+2, 3*j, 3*j+1, 3*j+2]
        K[np.ix_(idx, idx)] += kg
        F[3*i+1] -= q * L / 2; F[3*j+1] -= q * L / 2
    i_bot = n * 3 // 4
    F[3*i_bot+1] -= P_fondo
    fijos = [0, 1, 3*(n//2), 3*(n//2)+1]
    libres = np.setdiff1d(np.arange(ndof), fijos)
    u = np.zeros(ndof); u[libres] = np.linalg.solve(K[np.ix_(libres, libres)], F[libres])
    # momento por diferencias de curvatura (aprox.) a partir de rotaciones nodales
    rot = u[2::3]; L = 2 * np.pi * R / n
    M = E * I_TUBO * np.abs(np.diff(np.r_[rot, rot[0]])) / L
    return u[3*i_bot+1], M.max(), xy, u


def fem_aro_fuera_plano(R, P_carga, n=144):
    """Aro horizontal (emparrillado), apoyos en theta=0 y 180° (w=0; giro sobre X fijo en un apoyo
    para eliminar el mecanismo), cargas verticales P en theta=90° y 270° + peso propio.
    Devuelve flecha máxima (m) y momento flector/torsor máximos."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    xy = np.c_[R * np.cos(th), R * np.sin(th)]
    ndof = 3 * n  # w, rx, ry
    K = np.zeros((ndof, ndof)); F = np.zeros(ndof)
    q = ML_TUBO * g
    for i in range(n):
        j = (i + 1) % n
        dx, dy = xy[j] - xy[i]; L = math.hypot(dx, dy); c, s = dx / L, dy / L
        EI, GJ = E * I_TUBO, G * J_TUBO
        # elemento de emparrillado local: dof (w, tx(torsion), ty(flexion))
        k = np.zeros((6, 6))
        k[np.ix_([1, 4], [1, 4])] = GJ / L * np.array([[1, -1], [-1, 1]])
        kb = np.array([[12, 6*L, -12, 6*L], [6*L, 4*L*L, -6*L, 2*L*L],
                       [-12, -6*L, 12, -6*L], [6*L, 2*L*L, -6*L, 4*L*L]]) * EI / L**3
        b = [0, 2, 3, 5]
        k[np.ix_(b, b)] += kb
        T = np.zeros((6, 6)); r = np.array([[1, 0, 0], [0, c, s], [0, -s, c]]); T[:3,:3] = r; T[3:,3:] = r
        kg = T.T @ k @ T
        idx = [3*i, 3*i+1, 3*i+2, 3*j, 3*j+1, 3*j+2]
        K[np.ix_(idx, idx)] += kg
        F[3*i] -= q * L / 2; F[3*j] -= q * L / 2
    for k_ in (n // 4, 3 * n // 4):
        F[3*k_] -= P_carga
    fijos = [0, 3*(n//2), 1]
    libres = np.setdiff1d(np.arange(ndof), fijos)
    u = np.zeros(ndof); u[libres] = np.linalg.solve(K[np.ix_(libres, libres)], F[libres])
    return np.abs(u[0::3]).max(), xy, u


W_carga_int = (M_POSTE + M_DRON) * g                 # sobre el fondo del aro interior
W_conj_int = (m_int + 2 * m_munon + M_POSTE + M_DRON) * g  # transmitido a los rodamientos del aro interior
casos = {
    "Reposo (dron apoyado, sin empuje)": W_carga_int,
    "Empuje máximo (T=2·peso, empuja hacia arriba)": W_carga_int - T_MAX,
}
fem_rows = []
res_fem = {}
for nombre, P in casos.items():
    d_int_, Mmax, xy_i, u_i = fem_aro_en_plano(R_INT, P)
    # aro exterior: recibe la reacción de cada pivote del aro interior
    P_piv = ((m_int + 2 * m_munon) * g + P) / 2
    d_ext_, xy_e, u_e = fem_aro_fuera_plano(R_EXT, P_piv)
    fem_rows.append((nombre, f"{P:.1f}", f"{d_int_*1e3:.3f}", f"{P_piv:.1f}", f"{d_ext_*1e3:.3f}"))
    res_fem[nombre] = (d_int_, d_ext_, xy_i, u_i, xy_e, u_e)
guardar("fem_aros.csv", fem_rows,
        ["caso", "carga_fondo_aro_int_N", "desp_vertical_fondo_aro_int_mm",
         "carga_por_pivote_aro_ext_N", "flecha_max_aro_ext_mm"])

# 5. Ejes y rodamientos --------------------------------------------------------
VOLADIZO = 0.040   # m, distancia rodamiento - unión soldada (*)
F_piv_int = W_conj_int / 2
F_piv_ext = (W_conj_int + (m_ext + 2 * m_eje_lat) * g) / 2
F_axial_yaw = W_conj_int + (m_ext + 2 * m_eje_lat + m_U + m_eje_U) * g  # sin platinas ni chumaceras
# en empuje máximo la reacción se invierte; se toma el mayor valor absoluto
F_piv_int_T = abs((m_int + 2 * m_munon + M_POSTE + M_DRON) * g - T_MAX) / 2

def sigma_flex(F, a_, d):
    return 32 * F * a_ / (math.pi * d**3)

ejes = [
    ("Muñón aro interior (Ø20 mm, balinera)", D_MUNON, max(F_piv_int, F_piv_int_T)),
    ("Eje lateral aro exterior (7/8\", chumacera de pie)", D_EJE, F_piv_ext),
]
eje_rows = []
for n_, d, F in ejes:
    s = sigma_flex(F, VOLADIZO, d)
    eje_rows.append((n_, f"{d*1e3:.2f}", f"{F:.1f}", f"{s/1e6:.2f}", f"{SY_EJE/s:.0f}"))
guardar("verificacion_ejes.csv", eje_rows,
        ["eje", "diametro_mm", "carga_radial_N", "esfuerzo_flexion_MPa", "factor_seguridad_fluencia"])

rod = [
    ("Rodamiento 6004 (aro interior) — C0=5,0 kN", 5000, max(F_piv_int, F_piv_int_T)),
    ("Chumacera de pie UCP205-14 (aro exterior) — C0≈7,85 kN", 7850, F_piv_ext),
    ("Chumacera plana UCFL205-14 (guiñada, carga axial) — C0≈7,85 kN", 7850, F_axial_yaw),
]
rod_rows = [(n_, f"{F:.1f}", f"{C0/F:.0f}") for n_, C0, F in rod]
guardar("verificacion_rodamientos.csv", rod_rows, ["rodamiento", "carga_N", "relacion_C0_carga"])

# ----------------------------------------------------------------------------- reporte
if __name__ == "__main__":
    print(f"Masa total calculada (aros+ejes+guía): {sum(m for _,_,m in masas)+M_POSTE:.2f} kg")
    print(f"Tubo 1/2\" cal16: A={A_TUBO*1e6:.1f} mm2  I={I_TUBO*1e12:.0f} mm4  masa lineal={ML_TUBO:.3f} kg/m")
    for n_, L, m in masas:
        print(f"  {n_}: L={L:.3f} m  m={m:.2f} kg")
    print("Inercias (kg·m2):")
    for eje, comp in inercia.items():
        print(f"  {eje}: total={sum(comp.values()):.3f}  {comp}")
    print(f"Dron ref.: Ixx=Iyy={I_dron_xy:.4f}  Izz={I_dron_z:.4f}")
    for eje, comp in inercia.items():
        Iref = I_dron_z if "Z" in eje else I_dron_xy
        print(f"  relación cardán/dron {eje}: {sum(comp.values())/Iref:.0f}x")
    print("FEM:")
    for r in fem_rows: print("  ", r)
    print("Ejes:")
    for r in eje_rows: print("  ", r)
    print("Rodamientos:")
    for r in rod_rows: print("  ", r)
    print(f"Par grav. max (h=0.20, 90°): {par_grav(np.pi/2, 0.20):.2f} N·m ; h=0: {par_grav(np.pi/2, 0):.2f}")
    # altura de equilibrio neutro
    h_neutro = (M_POSTE * g * L_POSTE / 2) / (M_DRON * g + M_POSTE * g / 2)
    print(f"Altura de equilibrio neutro sobre el centro: {h_neutro*100:.1f} cm")
    print(f"Carga axial guiñada: {F_axial_yaw:.1f} N; T_max={T_MAX:.1f} N")

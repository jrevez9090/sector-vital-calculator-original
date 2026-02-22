import streamlit as st
import re

st.set_page_config(page_title="Sector Vital Calculator", layout="centered")

st.title("Sector Vital Calculator (Valens Book IV)")

# ============================
# CSS STYLE
# ============================

st.markdown("""
<style>
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
input[type="number"] {
    border: 2px solid #555 !important;
    border-radius: 6px !important;
}

div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within,
input[type="number"]:focus {
    border: 2px solid #e74c3c !important;
    outline: none !important;
}

.green { color: #2ecc71; font-weight: 500; }
.red { color: #e74c3c; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.write("Enter prenatal lunation position and zodiac position for each planet.")
st.write("⚠ Use format like: 12º43'")

st.markdown("---")

# ============================
# STRUCTURE
# ============================

signs = [
    "Aries","Taurus","Gemini","Cancer",
    "Leo","Virgo","Libra","Scorpio",
    "Sagittarius","Capricorn","Aquarius","Pisces"
]

def sign_to_degree(sign, degree, minutes):
    return signs.index(sign) * 30 + degree + (minutes / 60)

def years_to_ymd(years):
    y = int(years)
    remaining = (years - y) * 12
    m = int(remaining)
    d = int((remaining - m) * 30)
    return y, m, d

def parse_position(text):
    if not text:
        return None, None
    text = text.strip().replace("°","º").replace("’","'")
    match = re.fullmatch(r"\s*(\d{1,2})º\s*(\d{1,2})'\s*", text)
    if match:
        deg = int(match.group(1))
        mins = int(match.group(2))
        if 0 <= deg <= 29 and 0 <= mins <= 59:
            return deg, mins
    return None, None

# ============================
# PRENATAL LUNATION
# ============================

st.markdown("### Prenatal Lunation Position")

col1, col2 = st.columns(2)

with col1:
    lun_sign = st.selectbox("Lunation Sign", signs)

with col2:
    lun_text = st.text_input("Lunation Position (format: 12º43')")

lun_degree = None
deg, mins = parse_position(lun_text)
if deg is not None:
    lun_degree = sign_to_degree(lun_sign, deg, mins)

st.markdown("---")

# ============================
# PLANETS
# ============================

planets = {}
planet_names = ["Saturn","Jupiter","Mars","Venus","Mercury","Sun","Moon"]

for planet in planet_names:
    col1, col2 = st.columns(2)

    with col1:
        sign = st.selectbox(f"{planet} Sign", signs, key=f"{planet}_sign")

    with col2:
        pos_text = st.text_input(f"{planet} Position (format: 12º43')", key=f"{planet}_pos")

    deg, mins = parse_position(pos_text)
    if deg is not None:
        planets[planet] = sign_to_degree(sign, deg, mins)
    else:
        planets[planet] = None

# ============================
# PERIODS
# ============================

periods = {
    "Saturn":30,
    "Jupiter":12,
    "Mars":15,
    "Venus":8,
    "Mercury":20,
    "Sun":19,
    "Moon":25
}

# ============================
# CALCULATION
# ============================

if st.button("Calculate"):

    if lun_degree is None or any(v is None for v in planets.values()):
        st.error("Please fill all fields correctly.")
        st.stop()

    sorted_planets = sorted(planets.items(), key=lambda x: x[1])

    afeta = None
    for name, degree in sorted_planets:
        if degree > lun_degree:
            afeta = name
            break
    if not afeta:
        afeta = sorted_planets[0][0]

    start_index = next(i for i,(n,_) in enumerate(sorted_planets) if n == afeta)
    ordered = sorted_planets[start_index:] + sorted_planets[:start_index]

    cycle1 = []
    cumulative = 0
    for name,_ in ordered:
        duration = periods[name] / 4
        cumulative += duration
        cycle1.append((name,duration,cumulative))

    st.session_state.cycle1 = cycle1
    st.session_state.afeta = afeta

# ============================
# DISPLAY
# ============================

if "cycle1" in st.session_state:

    cycle1 = st.session_state.cycle1
    cycle_length = cycle1[-1][2]

    def rebuild_cycle(cycle):
        cumulative = 0
        rebuilt = []
        for name,duration,_ in cycle:
            cumulative += duration
            rebuilt.append((name,duration,cumulative))
        return rebuilt

    cycle2_internal = rebuild_cycle(cycle1[1:] + cycle1[:1])
    cycle3_internal = rebuild_cycle(cycle2_internal[1:] + cycle2_internal[:1])

    st.markdown(f"### Initial Afeta: <span class='red'>{st.session_state.afeta}</span>", unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown("### 1st Cycle")
        for name,duration,cum in cycle1:
            y,m,d = years_to_ymd(duration)
            st.markdown(f"{name}<br><span class='green'>{y}y {m}m {d}d</span><br>(cumulative: <span class='green'>{round(cum,3)}</span>)", unsafe_allow_html=True)

    with colB:
        st.markdown("### 2nd Cycle")
        for name,duration,cum in cycle2_internal:
            absolute = cycle_length + cum
            y,m,d = years_to_ymd(duration)
            st.markdown(f"{name}<br><span class='green'>{y}y {m}m {d}d</span><br>(cumulative: <span class='green'>{round(absolute,3)}</span>)", unsafe_allow_html=True)

    with colC:
        st.markdown("### 3rd Cycle")
        for name,duration,cum in cycle3_internal:
            absolute = (cycle_length*2) + cum
            y,m,d = years_to_ymd(duration)
            st.markdown(f"{name}<br><span class='green'>{y}y {m}m {d}d</span><br>(cumulative: <span class='green'>{round(absolute,3)}</span>)", unsafe_allow_html=True)

    # ACTIVE CALCULATION
    age = st.number_input("Enter age to check active planet",0.0,120.0)

    completed_cycles = int(age // cycle_length)
    age_mod = age % cycle_length

    if completed_cycles == 0:
        active_cycle = cycle1
        cycle_number = 1
    elif completed_cycles == 1:
        active_cycle = cycle2_internal
        cycle_number = 2
    else:
        active_cycle = cycle3_internal
        cycle_number = 3

    st.markdown(f"### Active Cycle: <span class='red'>{cycle_number}</span>", unsafe_allow_html=True)
    st.markdown(f"Active Cycle Afeta: <span class='red'>{active_cycle[0][0]}</span>", unsafe_allow_html=True)

    prev = 0
    active_planet = None

    for name,duration,cum in active_cycle:
        if age_mod <= cum:
            active_planet = name
            time_in_main = age_mod - prev
            break
        prev = cum

    st.markdown(f"Active Planet: <span class='red'>{active_planet}</span>", unsafe_allow_html=True)

    # ---------- SUBPERIODS (VALENS ORIGINAL) ----------

valens_days = {
    "Saturn": 85,
    "Jupiter": 34,
    "Mars": 42.5,
    "Venus": 22.6667,
    "Mercury": 56.6667,
    "Sun": 53.6667,
    "Moon": 70.8333
}

total_days = sum(valens_days.values())

main_duration = periods[active_planet] / 4

start = next(i for i,(n,_,_) in enumerate(active_cycle) if n==active_planet)
sub_order = active_cycle[start:] + active_cycle[:start]

cumulative_sub = 0
prev_sub = 0
sub_active = None

st.markdown("### Subperiods (Valens Original Method)")

for name,_,_ in sub_order:

    proportion = valens_days[name] / total_days
    sub_duration = main_duration * proportion
    cumulative_sub += sub_duration

    y2,m2,d2 = years_to_ymd(sub_duration)

    st.markdown(
        f"{name} - <span class='green'>{y2}y {m2}m {d2}d</span> "
        f"(cumulative: <span class='green'>{round(cumulative_sub,3)}</span>)",
        unsafe_allow_html=True
    )

    if sub_active is None and time_in_main <= cumulative_sub:
        sub_active = name
        time_inside_sub = time_in_main - prev_sub

    prev_sub = cumulative_sub
    prev_sub = 0
    sub_active = None

    st.markdown("### Subperiods")

    for name,_,_ in sub_order:
        proportion = fixed_days[name]/total_days
        sub_duration = main_duration*proportion
        cumulative_sub += sub_duration

        y2,m2,d2 = years_to_ymd(sub_duration)

        st.markdown(f"{name} - <span class='green'>{y2}y {m2}m {d2}d</span> (cumulative: <span class='green'>{round(cumulative_sub,3)}</span>)", unsafe_allow_html=True)

        if sub_active is None and time_in_main <= cumulative_sub:
            sub_active = name
            time_inside_sub = time_in_main - prev_sub

        prev_sub = cumulative_sub

    if sub_active:
        y3,m3,d3 = years_to_ymd(time_inside_sub)
        st.markdown(f"### Active Subperiod: <span class='red'>{sub_active}</span>", unsafe_allow_html=True)
        st.markdown(f"Elapsed inside subperiod: <span class='green'>{y3}y {m3}m {d3}d</span>", unsafe_allow_html=True)

st.markdown("---")
st.write("Made by Joana Revez")
st.write("Se for encontrado algum erro, reporte para joanarevez@hotmail.com")

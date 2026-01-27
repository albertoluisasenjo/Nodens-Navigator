"""
🌊 NODENS NAVIGATOR - Lovecraftian Flight Price Scraper
========================================================
Bringing order to the chaos of flight prices
A web app to find the best flight deals from Kiwi.com
"""

import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# =============================================================================
# PASSWORD AUTHENTICATION
# =============================================================================

def check_password():
    """Retorna True si el usuario ha introducido la contraseña correcta."""
    
    def password_entered():
        """Comprueba si la contraseña introducida es correcta."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # No almacenar la contraseña
        else:
            st.session_state["password_correct"] = False
    
    # Primera vez o contraseña incorrecta
    if "password_correct" not in st.session_state:
        # Mostrar input de contraseña
        st.markdown('<h1 class="main-title">🌊 Nodens Navigator</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Lord of the Great Abyss</p>', unsafe_allow_html=True)
        st.text_input(
            "🔐 Introduce la contraseña para acceder",
            type="password",
            on_change=password_entered,
            key="password",
            help="Contacta al administrador si no tienes acceso"
        )
        st.info("💡 La contraseña se configura en el archivo `.streamlit/secrets.toml`")
        return False
    
    # Contraseña incorrecta
    elif not st.session_state["password_correct"]:
        st.markdown('<h1 class="main-title">🌊 Nodens Navigator</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Lord of the Great Abyss</p>', unsafe_allow_html=True)
        st.text_input(
            "🔐 Introduce la contraseña para acceder",
            type="password",
            on_change=password_entered,
            key="password",
            help="Contacta al administrador si no tienes acceso"
        )
        st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
        return False
    
    # Contraseña correcta
    else:
        return True

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

# Page config with icon support
icon_path = Path("icon.png")
page_icon = str(icon_path) if icon_path.exists() else "🌊"

st.set_page_config(
    page_title="🌊 Nodens Navigator",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for responsive design - Nodens theme (ocean/abyss)
st.markdown("""
    <style>
    /* Main title styling */
    .main-title {
        font-size: clamp(1.5rem, 5vw, 3rem);
        text-align: center;
        color: #0a2463;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Subtitle */
    .subtitle {
        font-size: clamp(0.9rem, 2.5vw, 1.2rem);
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Card styling - Ocean depths gradient */
    .result-card {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        color: white;
        border: 1px solid rgba(100, 200, 255, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(6, 182, 212, 0.4);
    }
    
    .result-card h3 {
        margin-top: 0;
        color: #06b6d4;
        font-size: clamp(1.2rem, 3vw, 1.5rem);
    }
    
    .result-card a {
        color: #06b6d4 !important;
        text-decoration: none !important;
        font-weight: bold;
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.5rem 1rem;
        background: rgba(6, 182, 212, 0.1);
        border-radius: 6px;
        border: 1px solid rgba(6, 182, 212, 0.3);
        transition: all 0.2s ease;
        margin-top: 0.5rem;
    }
    
    .result-card a:hover {
        background: rgba(6, 182, 212, 0.2);
        border-color: #06b6d4;
        transform: translateX(3px);
    }
    
    .price-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #000;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: clamp(1.1rem, 3.5vw, 1.6rem);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    /* Responsive containers */
    .stButton>button {
        width: 100%;
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
    }
    
    /* Mobile optimization */
    @media (max-width: 768px) {
        .stTextInput>div>div>input {
            font-size: 16px !important;
        }
        .stSelectbox>div>div>select {
            font-size: 16px !important;
        }
        .result-card {
            padding: 1rem;
        }
    }
    
    /* Progress styling - Ocean wave */
    .stProgress > div > div > div > div {
        background: linear-gradient(to right, #0ea5e9, #06b6d4, #14b8a6);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 100%);
    }
    
    /* Day patterns table styling - compact */
    [data-testid="stSidebar"] .stSelectbox {
        margin-bottom: 0rem;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        font-size: 0.85rem !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox select {
        font-size: 0.85rem !important;
        padding: 0.25rem 0.5rem !important;
        min-height: 2rem !important;
    }
    
    /* Compact pattern display */
    div[data-testid="column"] p {
        margin-bottom: 0.25rem;
    }
    
    /* Make delete buttons smaller */
    [data-testid="stSidebar"] .stButton button {
        padding: 0.25rem 0.5rem !important;
        font-size: 1rem !important;
        min-height: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# PASSWORD CHECK - Stop here if not authenticated
# =============================================================================

if not check_password():
    st.stop()

# =============================================================================
# STREAMLIT UI - Only accessible after authentication
# =============================================================================

# =============================================================================
# CORE FUNCTIONS (from original script)
# =============================================================================

class KiwiURLBuilder:
    """Build Kiwi.com search URLs."""
    
    def __init__(self, base_url: str = "https://www.kiwi.com/es"):
        self.base_url = base_url
    
    def combine_day_patterns(self, patterns: List[str]) -> str:
        outbound_days = set()
        return_days = set()
        
        for pattern in patterns:
            out, ret = pattern.split('-')
            outbound_days.add(out)
            return_days.add(ret)
        
        outbound_str = ''.join(sorted(outbound_days))
        return_str = ''.join(sorted(return_days))
        
        return f"{outbound_str}-{return_str}"
    
    def build_search_url(
        self,
        origin: str,
        destination: str,
        outbound_dates: Tuple[str, str],
        return_dates: Tuple[str, str],
        combined_pattern: str,
        outbound_times: Tuple[int, int, int, int],
        return_times: Tuple[int, int, int, int],
        stops: bool
    ) -> str:
        outbound_date_str = f"{outbound_dates[0]}_{outbound_dates[1]}"
        return_date_str = f"{return_dates[0]}_{return_dates[1]}"
        
        times_str = (
            f"{outbound_times[0]}-{outbound_times[1]}-{outbound_times[2]}-{outbound_times[3]}_"
            f"{return_times[0]}-{return_times[1]}-{return_times[2]}-{return_times[3]}"
        )
        
        stop_str = "0%7Etrue" if not stops else "1%7Etrue"
        
        url = (
            f"{self.base_url}/search/results/{origin}/{destination}/"
            f"{outbound_date_str}/{return_date_str}/"
            f"?times={times_str}&daysInWeek={combined_pattern}&stopNumber={stop_str}"
        )
        
        return url
    
    def build_specific_url(
        self,
        origin: str,
        destination: str,
        outbound_date: str,
        return_date: str,
        outbound_times: Tuple[int, int, int, int],
        return_times: Tuple[int, int, int, int],
        stops: bool
    ) -> str:
        times_str = (
            f"{outbound_times[0]}-{outbound_times[1]}-{outbound_times[2]}-{outbound_times[3]}_"
            f"{return_times[0]}-{return_times[1]}-{return_times[2]}-{return_times[3]}"
        )
        
        stop_str = "0%7Etrue" if not stops else "1%7Etrue"
        
        url = (
            f"{self.base_url}/search/results/{origin}/{destination}/"
            f"{outbound_date}/{return_date}/"
            f"?times={times_str}&stopNumber={stop_str}"
        )
        
        return url


@st.cache_resource
def setup_driver(headless: bool = True) -> webdriver.Chrome:
    """Set up Chrome driver to mimic a real Windows browser."""
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType
    
    options = Options()
    
    # Headless mode (required for Streamlit Cloud)
    if headless:
        options.add_argument('--headless=new')
    
    # Minimal essential options for server environments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Anti-detection: disable automation flags
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Realistic Windows Chrome User Agent (latest stable)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Normal window size
    options.add_argument('--window-size=1920,1080')
    
    # Spanish language preference
    options.add_experimental_option('prefs', {
        'intl.accept_languages': 'es-ES,es;q=0.9,en;q=0.8'
    })
    
    try:
        # Try system chromium first (Streamlit Cloud)
        import subprocess
        try:
            chrome_version = subprocess.check_output(['chromium', '--version'], stderr=subprocess.DEVNULL).decode('utf-8')
            st.info(f"🌐 Chrome: {chrome_version.strip()}")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        except:
            st.info("🌐 Using Chrome")
            service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Remove webdriver property (anti-detection)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Override user agent via CDP (more reliable)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            "platform": "Win32"
        })
        
        return driver
        
    except Exception as e:
        st.error(f"❌ Chrome driver error: {str(e)}")
        st.warning("""
        **For Streamlit Cloud:**
        1. Ensure `packages.txt` contains:
           ```
           chromium
           chromium-driver
           ```
        2. Clear cache: Delete and redeploy
        
        **For local:**
        ```bash
        pip install --upgrade webdriver-manager selenium
        rm -rf ~/.wdm
        ```
        """)
        raise


def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    """Random delay."""
    time.sleep(random.uniform(min_sec, max_sec))


def human_click(driver, element):
    """Human-like click."""
    actions = ActionChains(driver)
    actions.move_to_element(element)
    random_delay(0.3, 0.8)
    actions.click(element)
    actions.perform()


def close_popup(driver):
    """Close popup if present."""
    try:
        random_delay(1, 2)
        close_btn = driver.find_element(By.CSS_SELECTOR, '[data-test="ModalCloseButton"]')
        human_click(driver, close_btn)
        random_delay(1, 2)
    except NoSuchElementException:
        pass


def extract_price(price_element) -> Optional[float]:
    try:
        text = price_element.text
        clean = text.replace('€', '').replace('$', '').replace(',', '.').replace('\xa0', '').strip()
        return float(clean)
    except:
        return None


def scrape_calendar(driver, wait, direction: str) -> List[dict]:
    prices = []
    try:
        calendars = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-test="CalendarContainer"]')))
        random_delay(1, 2)
        
        for calendar in calendars:
            days = calendar.find_elements(By.CSS_SELECTOR, '[data-test="CalendarDay"]')
            
            for day in days:
                try:
                    date = day.get_attribute('data-value')
                    price_elem = day.find_element(By.CSS_SELECTOR, '[data-test="NewDatepickerPrice"]')
                    price = extract_price(price_elem)
                    
                    if date and price:
                        prices.append({'Direction': direction, 'Date': date, 'Price': price})
                except:
                    continue
    except:
        pass
    
    return prices


def scrape_prices(driver, url: str) -> pd.DataFrame:
    """Scrape flight prices with robust error handling."""
    try:
        # Verify driver is alive
        try:
            _ = driver.current_url
        except Exception as e:
            st.error(f"❌ Driver not responding: {str(e)}")
            return pd.DataFrame()
        
        driver.get(url)
        random_delay(3, 5)
        close_popup(driver)
        
        wait = WebDriverWait(driver, 20)
        all_prices = []
        
        try:
            input_elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="SearchFieldDateInput"]')))
            human_click(driver, input_elem)
            random_delay(1, 2)
            all_prices.extend(scrape_calendar(driver, wait, 'Outbound'))
        except Exception as e:
            st.warning(f"⚠️ Outbound calendar error: {str(e)[:100]}")
        
        try:
            return_picker = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="DatePickerInput"]')))
            human_click(driver, return_picker)
            random_delay(1, 2)
            all_prices.extend(scrape_calendar(driver, wait, 'Return'))
        except Exception as e:
            st.warning(f"⚠️ Return calendar error: {str(e)[:100]}")
        
        if all_prices:
            return pd.DataFrame(all_prices)
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"❌ Major error in scrape_prices: {str(e)}")
        return pd.DataFrame()


def find_combinations(df: pd.DataFrame, day_pattern: str) -> pd.DataFrame:
    """Find flight combinations matching the day pattern (same week only)."""
    out_day, ret_day = map(int, day_pattern.split('-'))
    
    outbound = df[df['Direction'] == 'Outbound'].copy()
    return_df = df[df['Direction'] == 'Return'].copy()
    
    if outbound.empty or return_df.empty:
        return pd.DataFrame()
    
    outbound['Date'] = pd.to_datetime(outbound['Date'])
    return_df['Date'] = pd.to_datetime(return_df['Date'])
    
    outbound = outbound[outbound['Date'].dt.dayofweek == out_day]
    return_df = return_df[return_df['Date'].dt.dayofweek == ret_day]
    
    combinations = []
    for _, out_row in outbound.iterrows():
        # Only take returns within the SAME WEEK (max 7 days from outbound)
        valid_returns = return_df[
            (return_df['Date'] > out_row['Date']) & 
            (return_df['Date'] <= out_row['Date'] + pd.Timedelta(days=7))
        ]
        
        for _, ret_row in valid_returns.iterrows():
            days_diff = (ret_row['Date'] - out_row['Date']).days
            combinations.append({
                'Outbound_Date': out_row['Date'].strftime('%Y-%m-%d'),
                'Outbound_Price': out_row['Price'],
                'Return_Date': ret_row['Date'].strftime('%Y-%m-%d'),
                'Return_Price': ret_row['Price'],
                'Total_Price': out_row['Price'] + ret_row['Price'],
                'Days': days_diff
            })
    
    return pd.DataFrame(combinations)


# =============================================================================
# STREAMLIT UI
# =============================================================================

# Header
st.markdown('<h1 class="main-title">🌊 Nodens Navigator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Lord of the Great Abyss - Bringing order to the chaos of flight prices</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Origin
    origin = st.text_input(
        "🛫 Origin City",
        value="malaga-espana",
        help="Format: ciudad-pais (e.g., malaga-espana, barcelona-espana)"
    )
    
    # Destinations
    st.subheader("📍 Destination List")
    destinations_input = st.text_area(
        "Cities (one per line)",
        value="dusseldorf-alemania\nshannon-irlanda\nmemmingen-alemania",
        height=200,
        help="Format: ciudad-pais (e.g., dusseldorf-alemania, paris-francia)"
    )
    destinations = [d.strip().lower() for d in destinations_input.split('\n') if d.strip()]
    
    # Date range
    st.subheader("📅 Date Range")
    
    # Toggle for syncing return dates with outbound dates
    sync_dates = st.checkbox("🔗 Same date range for return", value=False, 
                              help="If checked, return dates will match outbound dates")
    
    col1, col2 = st.columns(2)
    with col1:
        outbound_start = st.date_input("Outbound from", datetime.now())
        if not sync_dates:
            return_start = st.date_input("Return from", datetime.now())
        else:
            return_start = outbound_start
            st.caption(f"Return from: {outbound_start.strftime('%Y-%m-%d')} (synced)")
    with col2:
        outbound_end = st.date_input("Outbound to", datetime.now() + timedelta(days=30))
        if not sync_dates:
            return_end = st.date_input("Return to", datetime.now() + timedelta(days=30))
        else:
            return_end = outbound_end
            st.caption(f"Return to: {outbound_end.strftime('%Y-%m-%d')} (synced)")
    
    # Day patterns
    st.subheader("📆 Day Patterns")
    
    # Initialize patterns in session state
    if 'day_patterns' not in st.session_state:
        st.session_state.day_patterns = [
            {'outbound': 'Fri', 'return': 'Sun'},
            {'outbound': 'Thu', 'return': 'Mon'}
        ]
    
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Display patterns table with compact layout
    patterns_to_remove = []
    for idx, pattern in enumerate(st.session_state.day_patterns):
        col1, col2, col3 = st.columns([4, 4, 1])
        
        with col1:
            outbound = st.selectbox(
                "Outbound",
                day_names,
                index=day_names.index(pattern['outbound']),
                key=f"out_{idx}",
                label_visibility="collapsed"
            )
            st.session_state.day_patterns[idx]['outbound'] = outbound
        
        with col2:
            return_day = st.selectbox(
                "Return",
                day_names,
                index=day_names.index(pattern['return']),
                key=f"ret_{idx}",
                label_visibility="collapsed"
            )
            st.session_state.day_patterns[idx]['return'] = return_day
        
        with col3:
            if st.button("×", key=f"del_{idx}", help="Remove pattern"):
                patterns_to_remove.append(idx)
        
        # Pattern name centered below the dropdowns
        pattern_name = f"{outbound[:3]}-{return_day[:3]}"
        st.markdown(
            f"<div style='text-align: center; font-size: 0.9rem; font-weight: bold; color: #06b6d4; margin: -0.8rem 0 1rem 0;'>"
            f"{pattern_name}</div>", 
            unsafe_allow_html=True
        )
    
    # Remove patterns
    for idx in reversed(patterns_to_remove):
        st.session_state.day_patterns.pop(idx)
    
    # Add new pattern button
    if st.button("➕ Add Pattern", use_container_width=True):
        st.session_state.day_patterns.append({'outbound': 'Fri', 'return': 'Sun'})
        st.rerun()
    
    # Build DAYS_IN_WEEK dict from patterns
    DAYS_IN_WEEK = {}
    for idx, pattern in enumerate(st.session_state.day_patterns):
        out_idx = day_names.index(pattern['outbound'])
        ret_idx = day_names.index(pattern['return'])
        pattern_name = f"{pattern['outbound'][:3]}-{pattern['return'][:3]}"
        DAYS_IN_WEEK[pattern_name] = [f"{out_idx}-{ret_idx}"]
    
    # Flight options
    st.subheader("✈️ Flight Options")
    allow_stops = st.checkbox("Allow connections", value=False)
    
    # Time preferences (simplified)
    st.subheader("🕐 Time Preferences")
    
    # Create hour options (0-24)
    hours = [f"{h:02d}:00" for h in range(25)]
    hour_values = list(range(25))
    
    st.markdown("**Outbound Flight**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Departure:")
        outbound_dep_after = st.selectbox(
            "Later than",
            hours,
            index=9,  # 09:00
            key="out_dep",
            label_visibility="visible"
        )
    with col2:
        st.markdown("Arrival:")
        outbound_arr_before = st.selectbox(
            "Earlier than",
            hours,
            index=16,  # 16:00
            key="out_arr",
            label_visibility="visible"
        )
    
    st.markdown("**Return Flight**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Departure:")
        return_dep_after = st.selectbox(
            "Later than",
            hours,
            index=13,  # 13:00
            key="ret_dep",
            label_visibility="visible"
        )
    with col2:
        st.markdown("Arrival:")
        return_arr_before = st.selectbox(
            "Earlier than",
            hours,
            index=21,  # 21:00
            key="ret_arr",
            label_visibility="visible"
        )
    
    # Convert to tuple format for Kiwi.com URL
    # Format: (departure_after, 24, 0, arrival_before)
    # Meaning: depart after X, anytime in the day (24), from midnight (0), arrive before Y
    outbound_dep_hour = hours.index(outbound_dep_after)
    outbound_arr_hour = hours.index(outbound_arr_before)
    return_dep_hour = hours.index(return_dep_after)
    return_arr_hour = hours.index(return_arr_before)
    
    outbound_times = (outbound_dep_hour, 24, 0, outbound_arr_hour)
    return_times = (return_dep_hour, 24, 0, return_arr_hour)

# Main area
if not destinations:
    st.warning("⚠️ Please add at least one destination in the sidebar")
elif not st.session_state.day_patterns:
    st.warning("⚠️ Please configure at least one day pattern in the sidebar")
else:
    # Display configuration summary
    with st.expander("📋 Search Summary", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        # Row 1: Origin spanning all columns
        st.markdown(f"**🛫 Origin:** {origin}")
        
        col1, col2 = st.columns(2)
        # Row 2: Date ranges
        with col1:
            st.metric("📅 Outbound Range", f"{(outbound_end - outbound_start).days} days")
        with col2:
            st.metric("📅 Return Range", f"{(return_end - return_start).days} days")
        
        col1, col2, col3 = st.columns(3)
        # Row 3: Patterns, Destinations, Connections
        with col1:
            pattern_list = [f"{p['outbound'][:3]}-{p['return'][:3]}" for p in st.session_state.day_patterns]
            st.metric("📆 Patterns", len(st.session_state.day_patterns))
            st.caption(", ".join(pattern_list))
        with col2:
            st.metric("📍 Destinations", len(destinations))
            if len(destinations) <= 3:
                st.caption(", ".join(destinations))
            else:
                st.caption(f"{', '.join(destinations[:3])}...")
        with col3:
            st.metric("✈️ Connections", "Allowed" if allow_stops else "Direct only")
    
    # Search button
    if st.button("🌊 Navigate the Abyss", type="primary", use_container_width=True):
        # Prepare data
        all_patterns = []
        for group_name, patterns in DAYS_IN_WEEK.items():
            all_patterns.extend(patterns)
        
        builder = KiwiURLBuilder()
        combined_pattern = builder.combine_day_patterns(all_patterns)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()
        
        all_destination_data = []
        scraping_stats = {
            'total': len(destinations),
            'completed': 0,
            'with_data': 0,
            'without_data': 0,
            'errors': 0
        }
        
        try:
            driver = setup_driver(headless=True)
            
            for idx, destination in enumerate(destinations):
                progress = (idx + 1) / len(destinations)
                progress_bar.progress(progress)
                status_text.text(f"🌊 Scraping {destination}... ({idx + 1}/{len(destinations)})")
                
                try:
                    # Verify driver is still alive before each request
                    try:
                        _ = driver.current_url
                    except:
                        try:
                            driver.quit()
                        except:
                            pass
                        driver = setup_driver(headless=True)
                    
                    url = builder.build_search_url(
                        origin=origin,
                        destination=destination,
                        outbound_dates=(
                            outbound_start.strftime('%Y-%m-%d'),
                            outbound_end.strftime('%Y-%m-%d')
                        ),
                        return_dates=(
                            return_start.strftime('%Y-%m-%d'),
                            return_end.strftime('%Y-%m-%d')
                        ),
                        combined_pattern=combined_pattern,
                        outbound_times=outbound_times,
                        return_times=return_times,
                        stops=allow_stops
                    )
                    
                    df = scrape_prices(driver, url)
                    
                    scraping_stats['completed'] += 1
                    
                    if not df.empty:
                        df['Destination'] = destination
                        all_destination_data.append(df)
                        scraping_stats['with_data'] += 1
                        
                        # Simple success message
                        results_container.info(
                            f"{destination}: {len(df)} prices found ({scraping_stats['with_data']}/{scraping_stats['completed']} destinations with data)"
                        )
                    else:
                        scraping_stats['without_data'] += 1
                        results_container.info(
                            f"{destination}: No prices found ({scraping_stats['with_data']}/{scraping_stats['completed']} destinations with data)"
                        )
                    
                    if idx < len(destinations) - 1:
                        time.sleep(random.uniform(5, 10))
                        
                except Exception as e:
                    scraping_stats['errors'] += 1
                    results_container.error(f"{destination}: Error - {str(e)[:50]}")
                    continue
            
            driver.quit()
            
            # Final message
            status_text.success("🌊 Nodens has brought order to the chaos!")
            
            st.info(f"""
            **📊 Scraping Summary:**
            - ✅ Completed: {scraping_stats['completed']}/{scraping_stats['total']}
            - 📈 With data: {scraping_stats['with_data']}
            - ⚠️ Without data: {scraping_stats['without_data']}
            - ❌ Errors: {scraping_stats['errors']}
            """)
            
            # Analyze combinations
            if all_destination_data:
                combinations_by_group = {group_name: [] for group_name in DAYS_IN_WEEK.keys()}
                
                for dest_df in all_destination_data:
                    destination = dest_df['Destination'].iloc[0]
                    
                    for group_name, patterns in DAYS_IN_WEEK.items():
                        for pattern in patterns:
                            combo_df = find_combinations(dest_df, pattern)
                            
                            if not combo_df.empty:
                                combo_df['Destination'] = destination
                                combo_df['Group'] = group_name
                                combinations_by_group[group_name].append(combo_df)
                
                # Display results
                has_results = any(len(combos) > 0 for combos in combinations_by_group.values())
                
                if has_results:
                    st.success("🎉 Nodens has brought order to the chaos!")
                    
                    # Best overall by group
                    st.subheader("🏆 Best Overall Deals")
                    
                    for group_name in DAYS_IN_WEEK.keys():
                        if combinations_by_group[group_name]:
                            group_df = pd.concat(combinations_by_group[group_name], ignore_index=True)
                            group_df = group_df.sort_values('Total_Price').reset_index(drop=True)
                            
                            best = group_df.iloc[0]
                            best_url = builder.build_specific_url(
                                origin=origin,
                                destination=best['Destination'],
                                outbound_date=best['Outbound_Date'],
                                return_date=best['Return_Date'],
                                outbound_times=outbound_times,
                                return_times=return_times,
                                stops=allow_stops
                            )
                            
                            st.markdown(f"""
                            <div class="result-card">
                                <h3>✈️ {best['Destination']}</h3>
                                <p><strong>{group_name.replace('_', ' ').title()}</strong></p>
                                <p>📅 {best['Outbound_Date']} → {best['Return_Date']} ({best['Days']} days)</p>
                                <p class="price-badge">💰 {best['Total_Price']:.0f} EUR</p>
                                <p><a href="{best_url}" target="_blank" style="color: #06b6d4; text-decoration: none; font-weight: bold;">🔗 Ver en Kiwi.com</a></p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Best by destination
                    st.subheader("📍 Best Deals by Destination")
                    
                    destination_results = {}
                    for destination in destinations:
                        destination_results[destination] = {}
                        
                        for group_name in DAYS_IN_WEEK.keys():
                            if combinations_by_group[group_name]:
                                group_df = pd.concat(combinations_by_group[group_name], ignore_index=True)
                                dest_df = group_df[group_df['Destination'] == destination]
                                
                                if not dest_df.empty:
                                    best = dest_df.sort_values('Total_Price').iloc[0]
                                    destination_results[destination][group_name] = best
                    
                    # Sort by cheapest
                    dest_min_prices = []
                    for destination in destinations:
                        if destination_results[destination]:
                            min_price = min(row['Total_Price'] for row in destination_results[destination].values())
                            dest_min_prices.append((destination, min_price))
                    
                    dest_min_prices.sort(key=lambda x: x[1])
                    
                    for destination, _ in dest_min_prices:
                        with st.expander(f"✈️ {destination}", expanded=False):
                            for group_name in DAYS_IN_WEEK.keys():
                                if group_name in destination_results[destination]:
                                    best = destination_results[destination][group_name]
                                    dest_url = builder.build_specific_url(
                                        origin=origin,
                                        destination=best['Destination'],
                                        outbound_date=best['Outbound_Date'],
                                        return_date=best['Return_Date'],
                                        outbound_times=outbound_times,
                                        return_times=return_times,
                                        stops=allow_stops
                                    )
                                    
                                    st.markdown(f"""
                                    **{group_name.replace('_', ' ').title()}**  
                                    📅 {best['Outbound_Date']} → {best['Return_Date']} ({best['Days']} días)  
                                    💰 **{best['Total_Price']:.0f} EUR** • [🔗 Ver vuelo]({dest_url})
                                    """)
                                    st.divider()
                    
                    # Best by pattern
                    st.subheader("📆 Best Deals by Pattern")
                    
                    for group_name in DAYS_IN_WEEK.keys():
                        if combinations_by_group[group_name]:
                            with st.expander(f"🗓️ {group_name.replace('_', ' ').title()}", expanded=False):
                                group_df = pd.concat(combinations_by_group[group_name], ignore_index=True)
                                
                                # Get best price per destination for this pattern
                                pattern_results = []
                                for destination in destinations:
                                    dest_df = group_df[group_df['Destination'] == destination]
                                    if not dest_df.empty:
                                        best = dest_df.sort_values('Total_Price').iloc[0]
                                        pattern_results.append(best)
                                
                                # Sort by price
                                pattern_results = sorted(pattern_results, key=lambda x: x['Total_Price'])
                                
                                # Display each destination's best deal for this pattern
                                for best in pattern_results:
                                    pattern_url = builder.build_specific_url(
                                        origin=origin,
                                        destination=best['Destination'],
                                        outbound_date=best['Outbound_Date'],
                                        return_date=best['Return_Date'],
                                        outbound_times=outbound_times,
                                        return_times=return_times,
                                        stops=allow_stops
                                    )
                                    
                                    st.markdown(f"""
                                    **{best['Destination']}**  
                                    📅 {best['Outbound_Date']} → {best['Return_Date']} ({best['Days']} días)  
                                    💰 **{best['Total_Price']:.0f} EUR** • [🔗 Ver vuelo]({pattern_url})
                                    """)
                                    st.divider()
                    
                    # Download results
                    all_combos = []
                    for group_name, combos in combinations_by_group.items():
                        if combos:
                            all_combos.extend(combos)
                    
                    if all_combos:
                        final_df = pd.concat(all_combos, ignore_index=True)
                        csv = final_df.to_csv(index=False).encode('utf-8')
                        
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv,
                            file_name=f"nodens_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.warning("😔 No valid combinations found. Try adjusting your search parameters.")
            else:
                st.error("❌ No data retrieved from any destination.")
                
                # Diagnostic information
                st.warning("""
                **🔍 Possible causes:**
                
                1. **Date range issues:**
                   - Verify your date ranges are in the future
                   - Ensure return dates are after outbound dates
                   - Try wider date ranges (30+ days)
                
                2. **City format issues:**
                   - Check format is `ciudad-pais` in Spanish (lowercase, no accents)
                   - Example: `dusseldorf-alemania` not `DUS` or `Düsseldorf-Germany`
                   - Verify cities in CITY_FORMAT_REFERENCE.md
                
                3. **Time restrictions:**
                   - Very narrow time ranges may have no flights
                   - Try expanding time ranges (e.g., 0:00-24:00)
                
                4. **Pattern issues:**
                   - Verify your day patterns make sense
                   - Return day should typically be after outbound day
                
                5. **Website blocking:**
                   - Kiwi.com may be blocking automated access
                   - Try fewer destinations at once
                   - Wait a few minutes and try again
                
                **💡 Quick fixes to try:**
                - Use default examples: `malaga-espana` → `dusseldorf-alemania`
                - Expand date ranges to 30+ days
                - Use time ranges: 0:00-24:00 for both directions
                - Try with just 1-2 destinations first
                """)
                
                # Show what was attempted
                with st.expander("🔧 Debug Information"):
                    st.code(f"""
Origin: {origin}
Destinations: {', '.join(destinations)}
Outbound dates: {outbound_start} to {outbound_end}
Return dates: {return_start} to {return_end}
Patterns: {[f"{p['outbound']}-{p['return']}" for p in st.session_state.day_patterns]}
Outbound times: {outbound_times}
Return times: {return_times}
Allow stops: {allow_stops}
                    """)
                    
                    st.markdown("**Example URL that was used:**")
                    example_url = builder.build_search_url(
                        origin=origin,
                        destination=destinations[0] if destinations else "dusseldorf-alemania",
                        outbound_dates=(
                            outbound_start.strftime('%Y-%m-%d'),
                            outbound_end.strftime('%Y-%m-%d')
                        ),
                        return_dates=(
                            return_start.strftime('%Y-%m-%d'),
                            return_end.strftime('%Y-%m-%d')
                        ),
                        combined_pattern=combined_pattern,
                        outbound_times=outbound_times,
                        return_times=return_times,
                        stops=allow_stops
                    )
                    st.code(example_url)
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            try:
                driver.quit()
            except:
                pass

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🌊 Nodens Navigator - Lord of the Great Abyss</p>
    <p><em>"From the depths of chaos, Nodens brings order and guides travelers home..."</em></p>
    <p style="font-size: 0.8rem; margin-top: 1rem;">Inspired by H.P. Lovecraft's cosmic mythology</p>
</div>
""", unsafe_allow_html=True)

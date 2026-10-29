import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import create_engine, text


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="𝐖𝐚𝐭𝐜𝐡𝐞𝐝 𝐋𝐢𝐛𝐫𝐚𝐫𝐲",
    page_icon="🎥",
    layout="wide"
)


# =========================================================
# AUTHENTICATION
# =========================================================

if not st.user.is_logged_in:

    st.title("🎥 Watched Library")

    st.write(
        "Sign in with Google to access your personal library."
    )

    if st.button("Continue with Google"):
        st.login("google")

    st.stop()


user_id = str(st.user.sub)

user_name = getattr(st.user, "name", "User")
user_email = getattr(st.user, "email", "")

# =========================================================
# GENRE COLORS
# =========================================================
genre_colors = {
    "Action": "#C44545",
    "Adventure": "#C8753D",
    "Comedy": "#C99A2E",
    "Drama": "#7656A8",
    "Fantasy": "#5369B8",
    "Horror": "#7D3038",
    "Mystery": "#485A75",
    "Romance": "#C45C82",
    "Sci-Fi": "#367C8D",
    "Thriller": "#59606F",
    "Other": "#66666F"
}


# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background-color: rgb(25, 29, 45);
    color: white;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

[data-testid="stSidebar"] {
    background: #55555D !important;
}


/* Sidebar text */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: white !important;
}


/* =====================================================
   LABELS
   ===================================================== */

[data-testid="stWidgetLabel"] p {
    color: white !important;
}


/* =====================================================
   INPUT FIELDS
   ===================================================== */

input,
textarea {
    background: rgb(245, 245, 248) !important;
    color: #191D2D !important;

    border: none !important;
    border-radius: 10px !important;
}


input::placeholder,
textarea::placeholder {
    color: rgba(25, 29, 45, 0.5) !important;
}


/* =====================================================
   SELECT BOXES
   ===================================================== */

div[data-baseweb="select"] {
    background: white !important;
    border-radius: 10px !important;
}


div[data-baseweb="select"] * {
    color: #191D2D !important;
}


/* Dropdown */
div[role="listbox"] {
    background: white !important;
}


div[role="option"] {
    color: #191D2D !important;
}


/* =====================================================
   NORMAL BUTTONS
   ===================================================== */

div.stButton > button,
div.stFormSubmitButton > button {

    background: #55555D;

    color: white;

    border: 1px solid #686872;

    border-radius: 8px;

    transition: 0.2s;
}


div.stButton > button:hover,
div.stFormSubmitButton > button:hover {

    background: #686872;

    color: white;

    border-color: #686872;
}


/* =====================================================
   STAR BUTTONS
   ===================================================== */

[data-testid="stSidebar"] div.stButton > button {

    color: white !important;

    font-size: 20px !important;

    text-align: center !important;
}


/* =====================================================
   METRICS
   ===================================================== */

[data-testid="stMetric"] {

    background-color: #55555D;

    padding: 15px;

    border-radius: 12px;
}


[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {

    color: white;
}


/* Hide genre marker */
.genre-marker {
    display: none;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
# =========================================================
# DATABASE_URL must be stored in Streamlit Secrets.
#
# Example:
#
# DATABASE_URL = "postgresql+psycopg2://..."
#
# Never put the real database password directly in this file.

engine = create_engine(
    st.secrets["DATABASE_URL"],
    pool_pre_ping=True
)


# =========================================================
# CREATE DATABASE TABLE
# =========================================================
# PostgreSQL version of your original media table.
#
# Every entry now has a user_id.
# This is what separates each user's library.

with engine.begin() as conn:

    conn.execute(
        text("""
            CREATE TABLE IF NOT EXISTS media (

                id BIGSERIAL PRIMARY KEY,

                user_id TEXT NOT NULL,

                title TEXT NOT NULL,

                category TEXT,

                genre TEXT,

                rating INTEGER,

                watched_date DATE,

                review TEXT,

                created_at TIMESTAMPTZ
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)
    )

    # Makes loading a user's library faster.
    conn.execute(
        text("""
            CREATE INDEX IF NOT EXISTS
            idx_media_user_id
            ON media(user_id)
        """)
    )


# =========================================================
# SESSION STATE
# =========================================================

if "selected_id" not in st.session_state:

    st.session_state.selected_id = None


if "editing_id" not in st.session_state:

    st.session_state.editing_id = None


if "add_rating" not in st.session_state:

    st.session_state.add_rating = 5


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def load_data(current_user_id):

    query = text("""
        SELECT
            id,
            user_id,
            title,
            category,
            genre,
            rating,
            watched_date,
            review,
            created_at

        FROM media

        WHERE user_id = :user_id

        ORDER BY watched_date DESC,
                 id DESC
    """)

    return pd.read_sql(
        query,
        engine,
        params={
            "user_id": current_user_id
        }
    )


# ---------------------------------------------------------
# ADD ENTRY
# ---------------------------------------------------------

def add_entry(
    current_user_id,
    title,
    category,
    genre,
    rating,
    watched_date,
    review
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO media (
                    user_id,
                    title,
                    category,
                    genre,
                    rating,
                    watched_date,
                    review
                )

                VALUES (
                    :user_id,
                    :title,
                    :category,
                    :genre,
                    :rating,
                    :watched_date,
                    :review
                )
            """),

            {
                "user_id":
                    current_user_id,

                "title":
                    title,

                "category":
                    category,

                "genre":
                    genre,

                "rating":
                    rating,

                "watched_date":
                    watched_date,

                "review":
                    review
            }
        )


# ---------------------------------------------------------
# UPDATE ENTRY
# ---------------------------------------------------------

def update_entry(
    current_user_id,
    entry_id,
    title,
    rating,
    category,
    genre,
    review
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                UPDATE media

                SET
                    title = :title,
                    rating = :rating,
                    category = :category,
                    genre = :genre,
                    review = :review

                WHERE id = :id
                AND user_id = :user_id
            """),

            {
                "title":
                    title,

                "rating":
                    rating,

                "category":
                    category,

                "genre":
                    genre,

                "review":
                    review,

                "id":
                    entry_id,

                "user_id":
                    current_user_id
            }
        )


# ---------------------------------------------------------
# DELETE ENTRY
# ---------------------------------------------------------

def delete_entry(
    current_user_id,
    entry_id
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM media

                WHERE id = :id
                AND user_id = :user_id
            """),

            {
                "id":
                    entry_id,

                "user_id":
                    current_user_id
            }
        )


# =========================================================
# STAR RATING
# =========================================================

def star_rating_picker():

    if "add_rating" not in st.session_state:

        st.session_state.add_rating = 5


    st.markdown(
        f"""
        <div style="
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            color: white;
            margin-bottom: 8px;
        ">
            Selected Rating:
            {st.session_state.add_rating}/5
        </div>
        """,
        unsafe_allow_html=True
    )


    cols = st.columns(5)


    for i in range(1, 6):

        with cols[i - 1]:

            star = (
                "★"
                if i <= st.session_state.add_rating
                else "☆"
            )


            if st.button(
                star,
                key=f"rating_{i}",
                use_container_width=True
            ):

                st.session_state.add_rating = i

                st.rerun()


    return st.session_state.add_rating


def get_badges(df):

    badges = []
    count = len(df)

    # Overall collection milestones: count all entries
    if count >= 1:
        badges.append("🎬 First Entry")

    if count >= 5:
        badges.append("🌱 Getting Started")

    if count >= 25:
        badges.append("🏆 Collector")

    if count >= 50:
        badges.append("🔥 Power User")

    if count >= 100:
        badges.append("💎 Ultimate Collector")

    if count >= 250:
        badges.append("👑 Library Legend")

    # Rating achievements
    ratings = pd.to_numeric(df.get("rating"), errors="coerce")
    if ratings.notna().any() and (ratings >= 5).any():
        badges.append("⭐ Five-Star Favourite")

    if ratings.notna().any() and (ratings >= 4).sum() >= 10:
        badges.append("🌟 Quality Seeker")

    # Genre exploration achievements
    genres = df["genre"].dropna() if "genre" in df.columns else pd.Series(dtype=str)
    unique_genres = genres.nunique()

    if unique_genres >= 3:
        badges.append("🧭 Genre Explorer")

    if unique_genres >= 6:
        badges.append("🌈 Genre Adventurer")

    # Category-specific achievements: thresholds count entries in that category only
    categories = (
        df["category"].fillna("").astype(str).str.strip().str.lower()
        if "category" in df.columns
        else pd.Series(dtype=str)
    )

    category_badges = {
        "movie": [
            (1, "🎞️ Movie Starter"),
            (10, "🍿 Movie Lover"),
            (25, "🎥 Movie Buff"),
            (50, "🎬 Cinema Legend"),
        ],
        "anime": [
            (1, "🌸 Anime Starter"),
            (10, "⛩️ Anime Fan"),
            (25, "⚔️ Anime Expert"),
            (50, "👑 Anime Legend"),
        ],
        "manga": [
            (1, "📖 Manga Starter"),
            (10, "📚 Manga Reader"),
            (25, "🖋️ Manga Collector"),
            (50, "🏯 Manga Legend"),
        ],
        "manhwa": [
            (1, "🪷 Manhwa Starter"),
            (10, "🖋️ Manhwa Enthusiast"),
            (25, "📚 Manhwa Collector"),
            (50, "👑 Manhwa Legend"),
        ],
        "show": [
            (1, "📺 Show Starter"),
            (10, "🍿 Show Watcher"),
            (25, "📺 Show Enthusiast"),
            (50, "🌟 Show Legend"),
        ],
        "series": [
            (1, "📺 Series Starter"),
            (10, "📺 Series Binger"),
            (25, "🎭 Series Enthusiast"),
            (50, "🏆 Series Legend"),
        ],
    }

    for category, milestones in category_badges.items():
        category_count = (categories == category).sum()
        for threshold, badge in milestones:
            if category_count >= threshold:
                badges.append(badge)

    # Review achievements: count entries with a non-empty review
    if "review" in df.columns:
        reviews = df["review"].fillna("").astype(str).str.strip()
        review_count = (reviews != "").sum()

        if review_count >= 5:
            badges.append("✍️ Thoughtful Reviewer")

        if review_count >= 20:
            badges.append("📝 Review Master")

    return badges



# =========================================================
# LOAD THIS USER'S DATA
# =========================================================

df = load_data(
    user_id
)


# =========================================================
# SIDEBAR — ACCOUNT
# =========================================================

with st.sidebar:

    st.subheader(
        "👤 Account"
    )


    st.write(
        f"**{user_name}**"
    )


    if user_email:

        st.caption(
            user_email
        )


    if st.button(
        "Log out",
        key="logout_button",
        use_container_width=True
    ):

        # Clear UI state before logging out.
        st.session_state.selected_id = None
        st.session_state.editing_id = None
        st.session_state.add_rating = 5

        st.logout()


    st.divider()


# =========================================================
# HEADER + BADGES
# =========================================================

header_col, badge_col = st.columns(2)


with header_col:

    st.title(
        "Watched Library 🎥🎟️🍿"
    )


with badge_col:

    st.subheader(
        "🏅 Your Badges"
    )


    badges = get_badges(df)


    if badges:

        badge_html = "".join(

            f"""
            <span style="
                background: #55555D;
                color: white;
                padding: 6px 10px;
                border-radius: 20px;
                margin: 4px;

# =========================================================
# SIDEBAR — ADD ENTRY
# =========================================================

with st.sidebar:

    st.header(
        "➕ Add Entry"
    )


    st.write(
        "**Rating**"
    )


    rating = star_rating_picker()


    with st.form(
        "add_form"
    ):


        title = st.text_input(
            "**Title**"
        )


        category = st.selectbox(
            "**Category**",

            [
                "Movie",
                "Anime",
                "Manga",
                "Show",
                "Series"
            ]
        )


        genre = st.selectbox(
            "**Genre**",

            [
                "Action",
                "Adventure",
                "Comedy",
                "Drama",
                "Fantasy",
                "Horror",
                "Mystery",
                "Romance",
                "Sci-Fi",
                "Thriller",
                "Other"
            ]
        )


        watched_date = st.date_input(
            "**Watched Date**",

            value=date.today()
        )


        review = st.text_area(
            "**Review**"
        )


        submitted = (
            st.form_submit_button(
                "Add"
            )
        )


    if submitted:


        if not title.strip():

            st.warning(
                "Please enter a title."
            )


        else:

            add_entry(
                current_user_id=user_id,

                title=title.strip(),

                category=category,

                genre=genre,

                rating=int(rating),

                watched_date=watched_date,

                review=review.strip()
            )


            st.session_state.add_rating = 5


            st.rerun()


# =========================================================
# EMPTY LIBRARY
# =========================================================

if df.empty:

    st.header(
        "Your Library"
    )

    st.info(
        "Your library is empty. Add your first entry 🎬"
    )

    st.stop()


# =========================================================
# FILTERS
# =========================================================

filter_dates = pd.to_datetime(
    df["watched_date"],
    errors="coerce"
)


# ---------------------------------------------------------
# YEAR OPTIONS
# ---------------------------------------------------------

year_options = (

    filter_dates
    .dt.year
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)


year_options = (

    ["All"]

    + sorted(
        year_options,
        reverse=True
    )
)


# ---------------------------------------------------------
# FILTER COLUMNS
# ---------------------------------------------------------

filter_col1, filter_col2, filter_col3, filter_col4 = (
    st.columns(4)
)


# YEAR
with filter_col1:

    year_filter = st.selectbox(
        "**Year**",
        year_options
    )


# CATEGORY
with filter_col2:

    category_options = (

        df["category"]
        .dropna()
        .unique()
        .tolist()
    )


    category_filter = st.selectbox(

        "**Category**",

        ["All"]
        + sorted(
            category_options
        )
    )


# GENRE
with filter_col3:

    genre_options = (

        df["genre"]
        .dropna()
        .unique()
        .tolist()
    )


    genre_filter = st.selectbox(

        "**Genre**",

        ["All"]
        + sorted(
            genre_options
        )
    )


# SEARCH
with filter_col4:

    search = st.text_input(
        "**Search Title**"
    )


# =========================================================
# APPLY FILTERS
# =========================================================

filtered = df.copy()


filtered["watched_date"] = pd.to_datetime(
    filtered["watched_date"],
    errors="coerce"
)


# YEAR
if year_filter != "All":

    filtered = filtered[

        filtered[
            "watched_date"
        ].dt.year

        == year_filter
    ]


# CATEGORY
if category_filter != "All":

    filtered = filtered[

        filtered["category"]
        == category_filter
    ]


# GENRE
if genre_filter != "All":

    filtered = filtered[

        filtered["genre"]
        == genre_filter
    ]


# SEARCH
if search.strip():

    filtered = filtered[

        filtered["title"]
        .str.contains(

            search.strip(),

            case=False,

            na=False
        )
    ]


# =========================================================
# EDIT ENTRY
# =========================================================

editing_id = (
    st.session_state.editing_id
)


if editing_id is not None:


    # df already contains only this user's records.
    selected = df[
        df["id"]
        == editing_id
    ]


    if not selected.empty:


        entry = selected.iloc[0]


        st.subheader(
            "✏️ Edit Entry"
        )


        new_title = st.text_input(

            "Title",

            value=str(
                entry["title"]
            ),

            key="edit_title"
        )


        new_rating = st.number_input(

            "Rating",

            min_value=1,

            max_value=5,

            value=int(
                entry["rating"]
            ),

            key="edit_rating"
        )


        categories = [

            "Movie",
            "Anime",
            "Manga",
            "Show",
            "Series"
        ]


        current_category = (
            entry["category"]
        )


        if current_category not in categories:

            current_category = "Movie"


        new_category = st.selectbox(

            "Category",

            categories,

            index=categories.index(
                current_category
            ),

            key="edit_category"
        )


        genres = [

            "Action",
            "Adventure",
            "Comedy",
            "Drama",
            "Fantasy",
            "Horror",
            "Mystery",
            "Romance",
            "Sci-Fi",
            "Thriller",
            "Other"
        ]


        current_genre = (
            entry["genre"]
        )


        if current_genre not in genres:

            current_genre = "Other"


        new_genre = st.selectbox(

            "Genre",

            genres,

            index=genres.index(
                current_genre
            ),

            key="edit_genre"
        )


        current_review = (
            entry["review"]
        )


        if pd.isna(
            current_review
        ):

            current_review = ""


        new_review = st.text_area(

            "Review",

            value=str(
                current_review
            ),

            key="edit_review"
        )


        save_col, cancel_col = (
            st.columns(2)
        )


        # SAVE
        with save_col:


            if st.button(
                "💾 Save Changes",
                use_container_width=True
            ):


                if not new_title.strip():

                    st.warning(
                        "Title cannot be empty."
                    )


                else:

                    update_entry(
                        current_user_id=user_id,

                        entry_id=editing_id,

                        title=new_title.strip(),

                        rating=int(
                            new_rating
                        ),

                        category=new_category,

                        genre=new_genre,

                        review=new_review.strip()
                    )


                    st.session_state.editing_id = None

                    st.session_state.selected_id = None


                    st.rerun()


        # CANCEL
        with cancel_col:


            if st.button(
                "❌ Cancel",
                use_container_width=True
            ):

                st.session_state.editing_id = None

                st.rerun()


    else:

        # If the ID is invalid or doesn't belong to this user,
        # close the editor.
        st.session_state.editing_id = None


# =========================================================
# LIBRARY
# =========================================================

st.header(
    "Your Library"
)


filtered = filtered.copy()


filtered["watched_date"] = pd.to_datetime(

    filtered["watched_date"],

    errors="coerce"
)


library_df = filtered.dropna(

    subset=[
        "watched_date"
    ]

).copy()


library_df = library_df.sort_values(

    "watched_date",

    ascending=False
)


# =========================================================
# DISPLAY LIBRARY
# =========================================================

if library_df.empty:


    st.info(
        "No entries found."
    )


else:


    library_df["month"] = (

        library_df[
            "watched_date"
        ]

        .dt.strftime(
            "%B %Y"
        )
    )


    # -----------------------------------------------------
    # GROUP BY MONTH
    # -----------------------------------------------------

    for month, month_df in library_df.groupby(

        "month",

        sort=False
    ):


        st.subheader(
            month
        )


        rows = month_df.to_dict(
            "records"
        )


        # -------------------------------------------------
        # 3 ENTRIES PER ROW
        # -------------------------------------------------

        for i in range(
            0,
            len(rows),
            3
        ):


            cols = st.columns(3)


            for col, row in zip(

                cols,

                rows[
                    i:i + 3
                ]
            ):


                with col:


                    # =====================================
                    # GENRE COLOR
                    # =====================================

                    genre_color = (
                        genre_colors.get(
                            row["genre"],
                            "#55555D"
                        )
                    )


                    entry_id = row["id"]

                    # =====================================
                    # INVISIBLE MARKER
                    # =====================================

                    st.markdown(
                        f"""
                        <div class="genre-marker genre-{entry_id}"></div>

                        <style>
                        .element-container:has(.genre-{entry_id})
                        + .element-container button {{
                            background-color: {genre_color} !important;
                            border-color: {genre_color} !important;
                            color: white !important;
                            font-weight: 600;
                            transition: 0.2s;
                        }}

                        .element-container:has(.genre-{entry_id})
                        + .element-container button:hover {{
                            filter: brightness(1.15);
                            color: white !important;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                    # =====================================
                    # TITLE BUTTON
                    # =====================================

                    if st.button(

                        row["title"],

                        key=
                            f"select_{entry_id}",

                        use_container_width=True
                    ):


                        if (
                            st.session_state.selected_id
                            == entry_id
                        ):

                            st.session_state.selected_id = None


                        else:

                            st.session_state.selected_id = entry_id


                        st.rerun()


                    # =====================================
                    # CATEGORY
                    # =====================================

                    st.write(
                        f"🎭 {row['category']}"
                    )


                    # =====================================
                    # GENRE
                    # =====================================

                    st.write(
                        f"🎬 {row['genre']}"
                    )


                    # =====================================
                    # RATING
                    # =====================================

                    st.write(
                        f"★ {row['rating']}/5"
                    )


                    # =====================================
                    # WATCHED DATE
                    # =====================================

                    st.write(

                        "📅 "

                        + row[
                            "watched_date"
                        ].strftime(
                            "%d %B %Y"
                        )
                    )


                    # =====================================
                    # SELECTED ENTRY
                    # =====================================

                    if (
                        st.session_state.selected_id
                        == entry_id
                    ):


                        review_text = row.get(
                            "review",
                            ""
                        )


                        if (
                            review_text
                            and not pd.isna(
                                review_text
                            )
                        ):

                            st.write(
                                f"📝 {review_text}"
                            )


                        edit_col, delete_col = (
                            st.columns(2)
                        )


                        # -----------------------------
                        # EDIT
                        # -----------------------------

                        with edit_col:


                            if st.button(

                                "✏️ Edit",

                                key=
                                    f"edit_{entry_id}",

                                use_container_width=True
                            ):


                                st.session_state.editing_id = entry_id


                                st.rerun()


                        # -----------------------------
                        # DELETE
                        # -----------------------------

                        with delete_col:


                            if st.button(

                                "🗑️ Delete",

                                key=
                                    f"delete_{entry_id}",

                                use_container_width=True
                            ):


                                delete_entry(
                                    current_user_id=user_id,
                                    entry_id=entry_id
                                )


                                st.session_state.selected_id = None

                                st.session_state.editing_id = None


                                st.rerun()


st.subheader(
    "📊 Stats"
)


stat1, stat2, stat3, stat4 = (
    st.columns(4)
)


# TOTAL
with stat1:

    st.metric(
        "Total",
        len(df)
    )


# AVERAGE RATING
with stat2:


    average_rating = pd.to_numeric(

        df["rating"],

        errors="coerce"

    ).mean()


    st.metric(

        "Average Rating",

        round(
            average_rating,
            1
        )

        if not pd.isna(
            average_rating
        )

        else 0
    )


# BEST RATING
with stat3:


    best_rating = pd.to_numeric(

        df["rating"],

        errors="coerce"

    ).max()


    st.metric(

        "Best Rating",

        int(
            best_rating
        )

        if not pd.isna(
            best_rating
        )

        else 0
    )


# BEST GENRE
with stat4:


    genre_mode = (

        df["genre"]

        .dropna()

        .mode()
    )


    best_genre = (

        genre_mode.iloc[0]

        if not genre_mode.empty

        else "N/A"
    )


    st.metric(
        "Best Genre",
        best_genre
    )

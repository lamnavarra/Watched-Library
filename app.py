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
# GENRE COLORS
# =========================================================
genre_colors = {
    "Action": "#C44545",       # Red
    "Adventure": "#C8753D",    # Orange
    "Comedy": "#C99A2E",       # Gold
    "Drama": "#7656A8",        # Purple
    "Fantasy": "#5369B8",      # Blue
    "Horror": "#7D3038",       # Dark Red
    "Mystery": "#485A75",      # Blue Gray
    "Romance": "#C45C82",      # Pink
    "Sci-Fi": "#367C8D",       # Teal
    "Thriller": "#59606F",     # Gray Blue
    "Other": "#66666F"         # Gray
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
engine = create_engine(
    "sqlite:///media.db"
)


with engine.begin() as conn:

    conn.execute(
        text("""
            CREATE TABLE IF NOT EXISTS media (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT NOT NULL,

                category TEXT,

                genre TEXT,

                rating INTEGER,

                watched_date TEXT,

                review TEXT
            )
        """)
    )


# =========================================================
# FIX OLD DATABASE
# =========================================================
with engine.begin() as conn:

    columns = conn.execute(
        text(
            "PRAGMA table_info(media)"
        )
    ).fetchall()


    column_names = [
        column[1]
        for column in columns
    ]


    if "review" not in column_names:

        conn.execute(
            text(
                "ALTER TABLE media ADD COLUMN review TEXT"
            )
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
# FUNCTIONS
# =========================================================

def load_data():

    return pd.read_sql(
        "SELECT * FROM media",
        engine
    )


# ---------------------------------------------------------
# STAR RATING
# ---------------------------------------------------------

def star_rating_picker():

    if "add_rating" not in st.session_state:

        st.session_state.add_rating = 5


    # Show current rating
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


# ---------------------------------------------------------
# BADGES
# ---------------------------------------------------------

def get_badges(df):

    badges = []

    count = len(df)


    if count >= 1:

        badges.append(
            "🎬 First Entry"
        )


    if count >= 10:

        badges.append(
            "🍿 Movie Lover"
        )


    if count >= 25:

        badges.append(
            "🏆 Collector"
        )


    if count >= 50:

        badges.append(
            "🔥 Power User"
        )


    return badges


# =========================================================
# LOAD DATA
# =========================================================

df = load_data()


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
                display: inline-block;
                font-size: 13px;
            ">
                {badge}
            </span>
            """

            for badge in badges
        )


        st.markdown(
            badge_html,
            unsafe_allow_html=True
        )


    else:

        st.markdown(
            """
            <span style="
                background: #55555D;
                color: white;
                padding: 6px 10px;
                border-radius: 20px;
                display: inline-block;
                font-size: 13px;
            ">
                No badges yet —
                start adding entries!
            </span>
            """,

            unsafe_allow_html=True
        )


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

            with engine.begin() as conn:

                conn.execute(

                    text("""
                        INSERT INTO media (
                            title,
                            category,
                            genre,
                            rating,
                            watched_date,
                            review
                        )

                        VALUES (
                            :title,
                            :category,
                            :genre,
                            :rating,
                            :watched_date,
                            :review
                        )
                    """),

                    {
                        "title":
                            title.strip(),

                        "category":
                            category,

                        "genre":
                            genre,

                        "rating":
                            int(rating),

                        "watched_date":
                            str(watched_date),

                        "review":
                            review.strip()
                    }
                )


            st.session_state.add_rating = 5


            st.rerun()


# =========================================================
# EMPTY LIBRARY
# =========================================================

if df.empty:

    st.info(
        "Add your first entry 🎬"
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
                            """),

                            {
                                "title":
                                    new_title.strip(),

                                "rating":
                                    int(new_rating),

                                "category":
                                    new_category,

                                "genre":
                                    new_genre,

                                "review":
                                    new_review.strip(),

                                "id":
                                    editing_id
                            }
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
                        <div
                            class="
                                genre-marker
                                genre-{entry_id}
                            "
                        ></div>

                        <style>

                        /*
                        Color the Streamlit button
                        immediately following this
                        genre marker.
                        */

                        .element-container:has(
                            .genre-{entry_id}
                        )
                        + .element-container
                        button {{

                            background-color:
                                {genre_color}
                                !important;

                            border-color:
                                {genre_color}
                                !important;

                            color:
                                white
                                !important;

                            font-weight:
                                600;

                            transition:
                                0.2s;
                        }}


                        .element-container:has(
                            .genre-{entry_id}
                        )
                        + .element-container
                        button:hover {{

                            filter:
                                brightness(1.15);

                            color:
                                white
                                !important;
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


                                with engine.begin() as conn:


                                    conn.execute(

                                        text("""
                                            DELETE FROM media
                                            WHERE id = :id
                                        """),

                                        {
                                            "id":
                                                entry_id
                                        }
                                    )


                                st.session_state.selected_id = None

                                st.session_state.editing_id = None


                                st.rerun()


# =========================================================
# STATS
# =========================================================

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



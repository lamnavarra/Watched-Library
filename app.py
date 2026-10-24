import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse


# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="𝐖𝐚𝐭𝐜𝐡𝐞𝐝 𝐋𝐢𝐛𝐫𝐚𝐫𝐲",
    page_icon="🎥",
    layout="wide"
)

st.markdown("""
<style>

/* APP BACKGROUND */
.stApp {
    background-color: rgb(25, 29, 45);
    color: white;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.08);
}

[data-testid="stSidebar"] * {
    color: black !important;
}

/* INPUT FIELDS */
input, textarea {
    background: rgb(245, 245, 248) !important;
    color: rgb(25, 29, 45) !important;
    border: none !important;
    border-radius: 10px !important;
}

input::placeholder,
textarea::placeholder {
    color: rgba(25, 29, 45, 0.5) !important;
}

/* SELECT BOXES */
div[data-baseweb="select"] {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 10px;
}

div[role="listbox"] {
    background: rgb(35, 40, 58);
    color: white;
}

/* BUTTONS */
div.stButton > button {
    background:  #55555D;
    color: white;
    border: 1px solid #55555D;
    border-radius: 8px;
}

div.stButton > button:hover {
    background:  #62626B;
}

            
/* Labels above fields */
[data-testid="stWidgetLabel"] p {
    color: white !important;
}

/* Text input */
input {
    color: #191D2D !important;
}

/* Selectbox text */
div[data-baseweb="select"] {
    color: #191D2D !important;
}
</style>
""", unsafe_allow_html=True)

   
# -----------------------------
# ACTION + BADGE SYSTEM
# -----------------------------
def update_badges_from_entries(df):
    count = len(df)

    st.session_state.badges = []

    if count >= 1:
        st.session_state.badges.append("🎬 First Entry")

    if count >= 10:
        st.session_state.badges.append("🍿 Movie Lover")

    if count >= 25:
        st.session_state.badges.append("🏆 Collector")

    if count >= 50:
        st.session_state.badges.append("🔥 Power User")

        st.rerun()


# -----------------------------
# STAR RATING
# -----------------------------
def star_rating_picker(key):
    if f"{key}_rating" not in st.session_state:
        st.session_state[f"{key}_rating"] = 5

    cols = st.columns(5)

    for i in range(1, 6):
        with cols[i - 1]:
            star = "★" if i <= st.session_state[f"{key}_rating"] else "☆"
            if st.button(star, key=f"{key}_{i}"):
                st.session_state[f"{key}_rating"] = i
                st.rerun()

    return st.session_state[f"{key}_rating"]

# -----------------------------
#SESSION STATE INIT
# -----------------------------
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None

if "badges" not in st.session_state:
    st.session_state.badges = []

if "actions_count" not in st.session_state:
    st.session_state.actions_count = 0

#-----------------------------
# TITLE + BADGES
#-----------------------------

col1, col2 = st.columns(2)

with col1:
    st.title("Watched Library 🎥🎟️🍿")

with col2:
    st.subheader("🏅 Your Badges")

    if st.session_state.badges:
        badge_html = "".join([
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
           for badge in st.session_state.badges
     ])

        st.markdown(badge_html, unsafe_allow_html=True)
    else:
     st.markdown("""
        <span style="
            background: #55555D;
            color: white;
            padding: 6px 10px;
            border-radius: 20px;
            margin: 4px;
            display: inline-block;
            font-size: 13px;
        ">
            No badges yet — start interacting!
        </span>
    """, unsafe_allow_html=True)


# -----------------------------
# ADD ENTRY
# -----------------------------
with st.sidebar:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
    background:  #55555D;  /* 50% opacity */
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)
    st.header("**➕ Add Entry**")

    st.write("**Rating**")
    rating = star_rating_picker("add")

    with st.form("add_form"):
        title = st.text_input("**Title**")

        category = st.selectbox(
            "**Category**",
            ["Movie", "Anime", "Manga", "Show", "Series"]
        )

        genre = st.selectbox(
            "**Genre**",
            ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller", "Other"]
        )

        watched_date = st.date_input("**Watched Date**", value=date.today())
        review = st.text_area("**Review**")

        submit = st.form_submit_button("Add")

        if submit and title.strip():

            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO media (title, category, genre, rating, watched_date, review)
                    VALUES (:title, :category, :genre, :rating, :watched_date, :review)
                """), {
                    "title": title,
                    "category": category,
                    "genre": genre,
                    "rating": int(rating),
                    "watched_date": str(watched_date),
                    "review": review
                })

            st.success("Added!")

            df = pd.read_sql("SELECT * FROM media", engine)
            update_badges_from_entries(df)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_sql("SELECT * FROM media", engine)
update_badges_from_entries(df)

if df.empty:
    st.info("Add your first entry 🎬")
    st.stop()

if "year_filter" not in st.session_state:
    st.session_state.year_filter = "All"
# -----------------------------
# FILTERS
# -----------------------------

st.markdown("""
<style>
div.stButton > button {
    color: white;
    background-color: #55555D;
    padding: 1px 6px;
    font-size: 11px;
    border-radius: 6px;
    min-height: 28px;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3,col4= st.columns(4)

with col1:
    # Remove missing years and convert years to integers
    year_options = (
        df["year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    year_options = ["All"] + sorted(
        year_options,
        reverse=True
    )

    year_filter = st.selectbox(
        "**Year**",
        year_options
    )
with col2:
    category_filter = st.selectbox(
        "**Category**",
        ["All"] + sorted(df["category"].unique())
    )

with col3:
    genre_filter = st.selectbox(
        "**Genre**",
        ["All"] + sorted(df["genre"].unique())
    )

with col4:
    search = st.text_input("**Search Title**")

# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered = df.copy()

if year_filter != "All":
    filtered = filtered[filtered["year"] == year_filter]

if category_filter != "All":
    filtered = filtered[filtered["category"] == category_filter]

if search:
    filtered = filtered[
        filtered["title"].str.contains(search, case=False, na=False)
    ]

# -----------------------------
# DISPLAY + EDIT + DELETE
# -----------------------------
st.header("Your Library")

st.markdown("""
<style>

/* LIBRARY CARD */
.card {
    background-color: #55555D;
    color: white;
    padding: 16px;
    border-radius: 14px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.20);
    transition: 0.2s;
}

/* CARD HOVER */
.card:hover {
    transform: scale(1.01);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.30);
}

/* BUTTONS */
div.stButton > button {
    width: 100%;
    background-color: #55555D;
    color: white;
    text-align: left;
    border: 1px solid #686872;
    border-radius: 10px;
    padding: 0.5rem;
    transition: 0.2s;
}

/* BUTTON HOVER */
div.stButton > button:hover {
    background-color: #686872;
    color: white;
    border-color: #686872;
}

/* SELECTED BUTTON */
.selected-btn button {
    background-color: #73737D !important;
    color: white !important;
    font-weight: 600;
    border: 2px solid #8A8A94 !important;
}

</style>
""", unsafe_allow_html=True)
editing_id = st.session_state.get("editing_id")

if editing_id is not None:

    movie = df[df["id"] == editing_id].iloc[0]

    st.subheader("Edit Entry")

    new_title = st.text_input(
        "Title",
        value=movie["title"]
    )

    new_rating = st.number_input(
        "Rating",
        min_value=1,
        max_value=5,
        value=int(movie["rating"])
    )

    categories = [
        "Movie",
        "Anime",
        "Manga",
        "Show",
        "Series"
    ]

    new_category = st.selectbox(
        "Category",
        categories,
        index=categories.index(movie["category"])
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

    new_genre = st.selectbox(
        "Genre",
        genres,
        index=genres.index(movie["genre"])
    )

    new_review = st.text_area(
        "Review",
        value=movie["review"]
    )

    col1, col2 = st.columns(2)

    # SAVE
    with col1:
        if st.button("💾 Save Changes"):

            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE media
                        SET title = :title,
                            rating = :rating,
                            category = :category,
                            genre = :genre,
                            review = :review
                        WHERE id = :id
                    """),
                    {
                        "title": new_title,
                        "rating": int(new_rating),
                        "category": new_category,
                        "genre": new_genre,
                        "review": new_review,
                        "id": editing_id
                    }
                )

            st.session_state.editing_id = None
            st.session_state.selected_id = None

            st.rerun()

    # CANCEL
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.editing_id = None
            st.rerun()


# Convert filtered dataframe to records
rows = filtered.to_dict("records")
    # Make sure watched_date is treated as a date
filtered = filtered.copy()
filtered["watched_date"] = pd.to_datetime(
    filtered["watched_date"],
    errors="coerce"
)

# Remove entries without a valid watched date
library_df = filtered.dropna(subset=["watched_date"]).copy()

# Sort newest first
library_df = library_df.sort_values(
    "watched_date",
    ascending=False
)

# Create month heading
library_df["month"] = library_df["watched_date"].dt.strftime(
    "%B %Y"
)

# Group library by month
for month, month_df in library_df.groupby(
    "month",
    sort=False
):

    st.subheader(month)

    rows = month_df.to_dict("records")

    # Display 3 entries per row
    for i in range(0, len(rows), 3):

        cols = st.columns(3)

        for col, row in zip(cols, rows[i:i+3]):

            with col:

                if st.button(
                    row["title"],
                    key=f"select_{row['id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_id = row["id"]

                st.write(f"🎭 {row['category']}")
                st.write(f"🎬 {row['genre']}")
                st.write(f"★ {row['rating']}/5")
                st.write(
                    f"📅 {row['watched_date'].strftime('%d %B %Y')}"
                )

                # Edit / Delete
                if st.session_state.selected_id == row["id"]:

                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button(
                            "✏️ Edit",
                            key=f"edit_{row['id']}"
                        ):
                            st.session_state.editing_id = row["id"]
                            st.rerun()

                    with c2:
                        if st.button(
                            "🗑️ Delete",
                            key=f"del_{row['id']}"
                        ):
                            with engine.begin() as conn:
                                conn.execute(
                                    text("""
                                        DELETE FROM media
                                        WHERE id = :id
                                    """),
                                    {"id": row["id"]}
                                )

                            st.rerun()


# -----------------------------
# STATS
# -----------------------------
st.subheader("📊 Stats")

# Style the metric boxes
st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #55555D;
    padding: 15px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: white;
}

[data-testid="stMetricValue"] {
    color: white;
}
</style>
""", unsafe_allow_html=True)


# Stats columns
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total",
        len(df)
    )

with c2:
    st.metric(
        "Average Rating",
        round(df["rating"].mean(), 1)
    )

with c3:
    st.metric(
        "Best Rating",
        df["rating"].max()
    )

with c4:
    st.metric(
        "Best Genre",
        df["genre"].mode()[0]
    )

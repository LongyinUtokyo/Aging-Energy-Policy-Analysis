from pipeline import blind_spots, build_taxonomy, merge_and_clean, preprocess_metadata, topic_trends


if __name__ == "__main__":
    cleaned, _ = merge_and_clean()
    preprocessed = preprocess_metadata(cleaned)
    taxonomy_df, _ = build_taxonomy(preprocessed)
    topic_year = topic_trends(preprocessed, taxonomy_df)
    blind_spots(preprocessed, taxonomy_df, topic_year)

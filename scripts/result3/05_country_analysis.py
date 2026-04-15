from pipeline import build_taxonomy, country_analysis, merge_and_clean, preprocess_metadata


if __name__ == "__main__":
    cleaned, _ = merge_and_clean()
    preprocessed = preprocess_metadata(cleaned)
    taxonomy_df, _ = build_taxonomy(preprocessed)
    country_analysis(preprocessed, taxonomy_df)

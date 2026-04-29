from pipeline import merge_and_clean, preprocess_metadata


if __name__ == "__main__":
    cleaned, _ = merge_and_clean()
    preprocess_metadata(cleaned)

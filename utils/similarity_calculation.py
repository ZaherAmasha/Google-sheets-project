import re


def preprocess_text(text):
    """Clean and normalize text for comparison"""
    # Convert to lowercase and remove special characters
    text = re.sub(r"[^\w\s]", "", str(text).lower())
    return text


def analyze_product_similarities(keyword, products):
    """Compare different similarity metrics for products"""
    # Preprocess keyword and products
    proc_keyword = preprocess_text(keyword)
    proc_products = [preprocess_text(p) for p in products]

    # Calculate weighted keyword presence
    def keyword_presence(product):
        """This similarity focuses on the search keywords and gives them a higher
        score if they:
        - appear earlier in the product name
        - contain an exact match of the search keyword(s) as the entire sequence
        - and if they are present as seperate words in the product name (how many keywords are in the title)
        """

        keyword_words = proc_keyword.split()
        product_words = product.split()

        # simple keyword presence, = (number of matched words) / (number of search keyword words)
        base_score = sum(1 for w in keyword_words if w in product_words) / len(
            keyword_words
        )

        # Check for exact phrase match, if so we assign a 50% bonus. for ex: if the keyword phrase is
        # 'black shoes', the score gets a 50% bonus if 'black shoes' exists as it is in the product name
        # this helps to differentiate (for example) between 'black shoes' and 'black shirt with shoes'.
        phrase_bonus = 1.5 if proc_keyword in product else 1.0

        # Position bonus - keywords appearing earlier get higher weight. The score is 1/position for each,
        # this way if the words of 'black shoes' appear earlier in the product's name, the score would be
        # higher. This creates a smooth decay in the score as the keywords appear later in the title.
        position_score = 0
        for i, word in enumerate(product_words):
            if word in keyword_words:
                position_score += 1 / (i + 1)
        # print(f"this is the base score for {proc_keyword}: {base_score}")
        # print(f"this is the phrase score for {proc_keyword}: {phrase_bonus}")
        # print(f"this is the position_score score for {proc_keyword}: {position_score}")

        # The (1 + (position_score/len(product_words))) is to consider the position score as a residual percentage.
        # like a 20% increase would mean a multiplication 1.2. The division by 1.5 is to get a full 1 score when the
        # keyword is exact match and normalize the rest of the possible scores accordingly. See the end for more details.
        final_score = (
            base_score * phrase_bonus * (1 + (position_score / len(product_words)))
        ) / 1.5
        # clipping values above 1 to get the final_score as a percentage
        if final_score > 1:
            final_score = 1.0

        return "%" + str(round(final_score, 3) * 100)  # as percentage

    keyword_scores = [keyword_presence(prod) for prod in proc_products]
    return keyword_scores


if __name__ == "__main__":
    # if you run this test code, you will see that the keyword similarity score for the title 'black shoes' is 2.625 and not 1 as
    # one might imagine (considering that the fetched product is the same as the keyword). Firstly, the phrase score is 1.5
    # (this title got the 50% bonus) because 'black shoes' is present as a sequence in the product title. Secondly, the position
    # score is also 1.5 because both search keyword words are present at the start of the sequence so they get a (1/(1+pos('black')) +
    # (1/(1+pos('shoes'))) = (1 + 0.5) = 1.5). I didn't want to include a check if the product title is the same as the search keyword
    # and then assign a %100 similarity to it because this would not consider the rest of the probable product titles. So to normalize the
    # entire range, I'm dividing the final score by 1.5, then clipping values that are more than 1 to 1. This is not ideal but it gives a good
    # enough estimate of the similarity.
    keyword = "black shoes"
    products = [
        "black shoes",
        "women's light running shoes Adult sneakers,net shoes, comfortable soft soled sneakers, women's breathable casual single shoes",
        "Nike Air Force 1 Men Woman Skateboard Shoes Fashion Black White Comfortable af1 Casual Sneakers Outdoor Flat Sports Trainers",
        "Men Casual Sport Shoes Light Sneakers White Outdoor Breathable Mesh Black Running Shoes Athletic Jogging Tennis Shoes",
        "leather Shoes Lace Men's Black Waxing British Business Martin boots Length Brown round Shoelace Women's Thin",
        "Black Men's Super Slim Fit Shirt Collar Honeycomb Single Pocket Covered Shirt TMNAW22GO0033",
        "Plated TPU Case With Lens Protector For iP15-6.1 inch JR-15Q1 - Blue",
    ]

    print(analyze_product_similarities(keyword, products))

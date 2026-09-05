import os
import logging
from dotenv import load_dotenv

load_dotenv()  # loads HF_TOKEN from .env into os.environ

# Suppress warnings from both huggingface_hub and semantic_router
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
os.environ["SEMANTIC_ROUTER_LOG_LEVEL"] = "ERROR"

from semantic_router import Route, SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(name='sentence-transformers/all-MiniLM-L6-v2')

faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "What is your policy on defective or damaged products?",

        "Can I return a product?",
        "How many days do I have to return an item?",
        "When will I receive my refund?",
        "How do I request a refund?",

        "Where is my order?",
        "Can I check the delivery status of my order?",
        "How do I track my shipment?",

        "Is cash on delivery available?",
        "Do you accept cash on delivery?",
        "Can I pay using COD?",
        "What payment options do you provide?",
        "Can I pay using a credit card?",
        "Can I pay using a debit card?",

        "What should I do if I receive a damaged product?",
        "My product is defective, what should I do?",
        "Can I replace a damaged item?",

        "How long does delivery take?",
        "When will my order be delivered?",
        "Can I cancel my order?",
        "How do I cancel an order?",
    ],
    score_threshold=0.3
)

sql = Route(
    name='sql',
    utterances=[
        "I want to buy nike shoes that have 50% discount",
        "Are there any shoes under Rs.3000",
        "Do you have formal shoes in size 9?",
        "Are there any puma shoes on sale?",
        "What is the price of puma running shoes?",
        "Show me shoes between Rs.1000 and Rs.5000",
        "Do you have pink puma shoes?",
    ],
    score_threshold=0.3
)

router = SemanticRouter(routes=[faq, sql], encoder=encoder)
router.sync("local")

if __name__ == '__main__':
    print(router("What is your policy on defective product").name)
    print(router("Pink Puma shoes in price range 1000 to 5000").name)


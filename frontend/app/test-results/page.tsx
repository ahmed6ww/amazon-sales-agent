"use client"

import React, { useState } from 'react';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronRight, Star, TrendingUp, Package, Search, Target } from 'lucide-react';

// Complete actual response data
const response = {
  "success": true,
  "asin": "http://amazon.com/dp/B0D5BL35MS",
  "marketplace": "US",
  "ai_analysis_keywords": {
    "success": true,
    "structured_data": {
      "product_context": {
        "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
        "brand": "Brewer Outdoor Solutions",
        "form": "Freeze-dried strawberry slices",
        "attributes": [
          "Organic",
          "No sugar added",
          "Gluten free"
        ],
        "pack_size": "4 Pack",
        "unit_size_each_oz": "1.2 oz",
        "use_cases": [
          "Baking",
          "Smoothies",
          "Cereals",
          "Travel",
          "Snacking"
        ]
      },
      "items": [
        {
          "phrase": "strawberry freeze dried",
          "search_volume": 424,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 4,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 689,
            "ranking_competitors": 9,
            "competitor_rank_avg": 14.1,
            "competitor_performance_score": 10
          }
        },
        {
          "phrase": "strawberries freeze dried",
          "search_volume": 303,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 728,
            "ranking_competitors": 9,
            "competitor_rank_avg": 15.2,
            "competitor_performance_score": 10
          }
        },
        {
          "phrase": "dried freeze strawberries",
          "search_volume": 204,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 643,
            "ranking_competitors": 9,
            "competitor_rank_avg": 15.7,
            "competitor_performance_score": 10
          }
        },
        {
          "phrase": "freeze-dried strawberries",
          "search_volume": 470,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 4,
          "intent_score": 2,
          "title_density": 4,
          "cpr": 8,
          "competition": {
            "competing_products": 548,
            "ranking_competitors": 9,
            "competitor_rank_avg": 15.9,
            "competitor_performance_score": 10
          }
        },
        {
          "phrase": "freeze dried strawberries bulk",
          "search_volume": 909,
          "root": "strawberry",
          "category": "Design-Specific",
          "relevancy_score": 3,
          "intent_score": 3,
          "title_density": 0,
          "cpr": 12,
          "competition": {
            "competing_products": 640,
            "ranking_competitors": 9,
            "competitor_rank_avg": 15.9,
            "competitor_performance_score": 10
          }
        },
        {
          "phrase": "freez dried apples",
          "search_volume": 159,
          "root": "apple",
          "category": "Irrelevant",
          "relevancy_score": 6,
          "intent_score": 0,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 433,
            "ranking_competitors": 6,
            "competitor_rank_avg": 8.3,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dried apples",
          "search_volume": 2686,
          "root": "apple",
          "category": "Irrelevant",
          "relevancy_score": 4,
          "intent_score": 0,
          "title_density": 2,
          "cpr": 28,
          "competition": {
            "competing_products": 417,
            "ranking_competitors": 6,
            "competitor_rank_avg": 8.8,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dried apple slices",
          "search_volume": 773,
          "root": "slice",
          "category": "Irrelevant",
          "relevancy_score": 6,
          "intent_score": 0,
          "title_density": 5,
          "cpr": 11,
          "competition": {
            "competing_products": 221,
            "ranking_competitors": 6,
            "competitor_rank_avg": 10.2,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dried apples bulk",
          "search_volume": 390,
          "root": "apple",
          "category": "Irrelevant",
          "relevancy_score": 6,
          "intent_score": 0,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 375,
            "ranking_competitors": 6,
            "competitor_rank_avg": 11.3,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dried strawberry",
          "search_volume": 847,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 5,
          "cpr": 11,
          "competition": {
            "competing_products": 632,
            "ranking_competitors": 9,
            "competitor_rank_avg": 16.4,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freezedried strawberry",
          "search_volume": 445,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 4,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 480,
            "ranking_competitors": 9,
            "competitor_rank_avg": 16.9,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dried strawberries organic",
          "search_volume": 422,
          "root": "strawberry",
          "category": "Design-Specific",
          "relevancy_score": 3,
          "intent_score": 3,
          "title_density": 1,
          "cpr": 8,
          "competition": {
            "competing_products": 404,
            "ranking_competitors": 9,
            "competitor_rank_avg": 16.9,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dry strawberry",
          "search_volume": 169,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 1000,
            "ranking_competitors": 9,
            "competitor_rank_avg": 17.8,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "strawberry chips",
          "search_volume": 371,
          "root": "chip",
          "category": "Design-Specific",
          "relevancy_score": 4,
          "intent_score": 2,
          "title_density": 1,
          "cpr": 8,
          "competition": {
            "competing_products": 205,
            "ranking_competitors": 8,
            "competitor_rank_avg": 18.1,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "dried strawberries 365",
          "search_volume": 219,
          "root": "strawberry",
          "category": "Branded",
          "relevancy_score": 4,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 214,
            "ranking_competitors": 9,
            "competitor_rank_avg": 18.8,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "simply nature freeze dried strawberries",
          "search_volume": 337,
          "root": "strawberry",
          "category": "Branded",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 196,
            "ranking_competitors": 9,
            "competitor_rank_avg": 19,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "nutristore freeze dried strawberries",
          "search_volume": 153,
          "root": "strawberry",
          "category": "Branded",
          "relevancy_score": 4,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 170,
            "ranking_competitors": 9,
            "competitor_rank_avg": 19.3,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dry strawberries",
          "search_volume": 433,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 618,
            "ranking_competitors": 9,
            "competitor_rank_avg": 19.8,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "dry strawberry fruit",
          "search_volume": 297,
          "root": "fruit",
          "category": "Relevant",
          "relevancy_score": 2,
          "intent_score": 2,
          "title_density": 2,
          "cpr": 8,
          "competition": {
            "competing_products": 2000,
            "ranking_competitors": 9,
            "competitor_rank_avg": 21,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dried organic strawberries",
          "search_volume": 242,
          "root": "strawberry",
          "category": "Design-Specific",
          "relevancy_score": 3,
          "intent_score": 3,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 371,
            "ranking_competitors": 9,
            "competitor_rank_avg": 21.2,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "dried strawberry slices",
          "search_volume": 355,
          "root": "slice",
          "category": "Design-Specific",
          "relevancy_score": 8,
          "intent_score": 3,
          "title_density": 6,
          "cpr": 8,
          "competition": {
            "competing_products": 324,
            "ranking_competitors": 9,
            "competitor_rank_avg": 48.9,
            "competitor_performance_score": 6
          }
        },
        {
          "phrase": "freeze dried strawberry slices",
          "search_volume": 713,
          "root": "slice",
          "category": "Design-Specific",
          "relevancy_score": 8,
          "intent_score": 3,
          "title_density": 4,
          "cpr": 10,
          "competition": {
            "competing_products": 301,
            "ranking_competitors": 9,
            "competitor_rank_avg": 36,
            "competitor_performance_score": 6
          }
        },
        {
          "phrase": "freeze dried strawberries slices",
          "search_volume": 415,
          "root": "slice",
          "category": "Design-Specific",
          "relevancy_score": 8,
          "intent_score": 3,
          "title_density": 2,
          "cpr": 8,
          "competition": {
            "competing_products": 297,
            "ranking_competitors": 9,
            "competitor_rank_avg": 33.1,
            "competitor_performance_score": 6
          }
        },
        {
          "phrase": "dehydrated strawberry slices",
          "search_volume": 250,
          "root": "slice",
          "category": "Design-Specific",
          "relevancy_score": 7,
          "intent_score": 3,
          "title_density": 4,
          "cpr": 8,
          "competition": {
            "competing_products": 240,
            "ranking_competitors": 9,
            "competitor_rank_avg": 54.8,
            "competitor_performance_score": 6
          }
        },
        {
          "phrase": "ruh roh freeze dried strawberry shortcake",
          "search_volume": 100,
          "root": "shortcake",
          "category": "Branded",
          "relevancy_score": 2,
          "intent_score": 1,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 65,
            "ranking_competitors": 5,
            "competitor_rank_avg": 21.8,
            "competitor_performance_score": 4.8
          }
        },
        {
          "phrase": "frozen sliced strawberries",
          "search_volume": 323,
          "root": "strawberry",
          "category": "Irrelevant",
          "relevancy_score": 5,
          "intent_score": 0,
          "title_density": 1,
          "cpr": 8,
          "competition": {
            "competing_products": 173,
            "ranking_competitors": 7,
            "competitor_rank_avg": 52.9,
            "competitor_performance_score": 4.8
          }
        },
        {
          "phrase": "dehydrated strawberries sliced",
          "search_volume": 130,
          "root": "strawberry",
          "category": "Design-Specific",
          "relevancy_score": 8,
          "intent_score": 3,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 175,
            "ranking_competitors": 9,
            "competitor_rank_avg": 73.7,
            "competitor_performance_score": 4
          }
        },
        {
          "phrase": "sliced strawberries",
          "search_volume": 351,
          "root": "strawberry",
          "category": "Outlier",
          "relevancy_score": 2,
          "intent_score": 1,
          "title_density": 8,
          "cpr": 8,
          "competition": {
            "competing_products": 131,
            "ranking_competitors": 4,
            "competitor_rank_avg": 46.8,
            "competitor_performance_score": 3.6
          }
        },
        {
          "phrase": "dried strawberries",
          "search_volume": 8603,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 5,
          "intent_score": 2,
          "title_density": 21,
          "cpr": 41,
          "competition": {
            "competing_products": 819,
            "ranking_competitors": 9,
            "competitor_rank_avg": 44.4,
            "competitor_performance_score": 6
          }
        },
        {
          "phrase": "free dried strawberries",
          "search_volume": 128,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 514,
            "ranking_competitors": 9,
            "competitor_rank_avg": 21.6,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freezer dried strawberries",
          "search_volume": 325,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 5,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 597,
            "ranking_competitors": 9,
            "competitor_rank_avg": 21.4,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "dehydrated strawberries bulk",
          "search_volume": 117,
          "root": "strawberry",
          "category": "Design-Specific",
          "relevancy_score": 3,
          "intent_score": 3,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 340,
            "ranking_competitors": 9,
            "competitor_rank_avg": 50.2,
            "competitor_performance_score": 6
          }
        },
        {
          "phrase": "dried strawberrries",
          "search_volume": 232,
          "root": "strawberry",
          "category": "Relevant",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 807,
            "ranking_competitors": 9,
            "competitor_rank_avg": 28.3,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "freeze dried strawberries freeze-dried strawberries slices",
          "search_volume": 101,
          "root": "slice",
          "category": "Design-Specific",
          "relevancy_score": 7,
          "intent_score": 3,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 312,
            "ranking_competitors": 9,
            "competitor_rank_avg": 27.9,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "fresas deshidratadas",
          "search_volume": 288,
          "root": "fresa",
          "category": "Spanish",
          "relevancy_score": 3,
          "intent_score": 2,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 93,
            "ranking_competitors": 9,
            "competitor_rank_avg": 39.9,
            "competitor_performance_score": 6
          }
        },
        {
          "phrase": "strawberry shortcake freeze dried",
          "search_volume": 129,
          "root": "shortcake",
          "category": "Irrelevant",
          "relevancy_score": 2,
          "intent_score": 1,
          "title_density": 0,
          "cpr": 8,
          "competition": {
            "competing_products": 178,
            "ranking_competitors": 5,
            "competitor_rank_avg": 30.8,
            "competitor_performance_score": 8
          }
        },
        {
          "phrase": "bulk freeze dried strawberries",
          "search_volume": 482,
          "root": "strawberry",
          "category": "Design-Specific",
          "relevancy_score": 2,
          "intent_score": 3,
          "title_density": 1,
          "cpr": 9,
          "competition": {
            "competing_products": 712,
            "ranking_competitors": 9,
            "competitor_rank_avg": 22.1,
            "competitor_performance_score": 8
          }
        }
      ],
      "stats": {
        "Relevant": {
          "count": 13,
          "examples": []
        },
        "Design-Specific": {
          "count": 12,
          "examples": []
        },
        "Irrelevant": {
          "count": 6,
          "examples": []
        },
        "Branded": {
          "count": 4,
          "examples": []
        },
        "Spanish": {
          "count": 1,
          "examples": []
        },
        "Outlier": {
          "count": 1,
          "examples": []
        }
      }
    },
    "final_output": "Keyword categorization completed",
    "scraped_product": {
      "url": "https://www.amazon.com/dp/B0D5BL35MS",
      "status": 200,
      "response_size": 1305613,
      "elements": {
        "productTitle": {
          "present": true,
          "text": [
            "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel"
          ]
        },
        "productOverview_feature_div": {
          "present": true,
          "kv": {
            "Item Weight": "4.8 Ounces",
            "Size": "4 Pack",
            "Brand": "Brewer Outdoor Solutions",
            "Package Weight": "0.19 Kilograms",
            "Number of Pieces": "4"
          }
        },
        "feature-bullets": {
          "present": true,
          "bullets": [
            "Delicious Flavor in Every Bite: Savor the naturally sweet, tangy crunch of freeze dried strawberry slices bursting with real fruit flavor. Enjoy Strawberry freeze dried as a fruity boost or add it to oatmeal, yogurt, smoothies, or desserts.",
            "Ideal Travel Companion: Lightweight, mess-free, and shelf-stable, our freeze dried strawberries bulk are perfect for hiking or camping, backpacking adventures. Enjoy this organic freeze dried fruit straight from the pouch or rehydrate for a fresh fruity treat.",
            "From Farm to Your Table: Our organic dried strawberries, delivered sun-ripened, farm-fresh, are made from real strawberries. No added sugar, no preservatives or GMOs - all natural dry strawberries with iron to help support immune health with every bite.",
            "Shelf Life: Our freeze-dried strawberries are at peak flavor for up to 24 months. For the best taste and texture in every bite, please enjoy within two year of purchase at anywhere at anytime.",
            "Bulk Packed for Convenience: Buy in bulk and enjoy premium quality freeze dried strawberries whenever you need them. Great for baking, snacking, or mixing with freeze dried fruit for a refreshing fruit combo."
          ]
        },
        "productDescription": {
          "present": false,
          "paragraphs": []
        },
        "prodDetails": {
          "present": false,
          "tech_specs": {},
          "additional_info": {}
        },
        "detailBullets_feature_div": {
          "present": true,
          "kv": {
            "Package Dimensions ‏ : ‎": "8.7 x 7.72 x 4.57 inches; 4.8 ounces",
            "Manufacturer ‏ : ‎": "Brewer Outdoor Solutions",
            "ASIN ‏ : ‎": "B0D5BL35MS",
            "Units ‏ : ‎": "4.8 Ounce",
            "Best Sellers Rank": "#71,397 in Grocery & Gourmet Food ( See Top 100 in Grocery & Gourmet Food ) #179 in Dried Berries",
            "Customer Reviews": "4.4 out of 5 stars 93 ratings"
          }
        },
        "aplus": {
          "present": true,
          "headings": [
            "From the brand",
            "Product description"
          ],
          "paragraphs": [],
          "list_items": []
        }
      },
      "images": {
        "present": true,
        "main_image": "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX385_PIbundle-4,TopRight,0,0_AA385SH20_.jpg",
        "all_images": [
          "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX385_PIbundle-4,TopRight,0,0_AA385SH20_.jpg",
          "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX466_PIbundle-4,TopRight,0,0_AA466SH20_.jpg",
          "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX679_PIbundle-4,TopRight,0,0_AA679SH20_.jpg",
          "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX425_PIbundle-4,TopRight,0,0_AA425SH20_.jpg",
          "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX342_PIbundle-4,TopRight,0,0_AA342SH20_.jpg",
          "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX522_PIbundle-4,TopRight,0,0_AA522SH20_.jpg",
          "https://m.media-amazon.com/images/I/81pgr0DuDOL._SX569_PIbundle-4,TopRight,0,0_AA569SH20_.jpg"
        ],
        "image_count": 7
      },
      "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
      "reviews": {
        "present": true,
        "sample_reviews": [
          "I purchased the 1.2oz bag for my family of 3 to try- I admit, I was tempted to buy the size \"small\" bag, to ensure Mama got an adequate sample, but then second guessed myself with the fear of them being too tart and no one enjoying them, as I've bought dried strawberries from a big box store before and they were pretty sour to eat and ended up wasting. Well, these proved me wrong!! It has the perfect amount of tart without being too sour to enjoy, and tastes just like a fresh strawberry in a crunchy enjoyable texture. Will definitely be getting the bigger bag! All of the family have tried the strawberries and agree they are a great snack and we need more! Buy some- In the BIG bag- you WON'T regret it!",
          "she was very happy. she said the flavor was excellent and finished the bag in 2 days (she also said they were kind of addictive due to their flavor). would recommend and will probably get her some more in a few weeks.",
          "Excellent quality. Large pieces of dehydrated strawberries. Very happy with purchase!",
          "These packages are not particularly large but on a cost-per ounce they are a good value.",
          "Ridiculously expensive"
        ],
        "review_highlights": [
          "4.4 out of 5 stars",
          "93 ratings"
        ]
      },
      "qa_section": {
        "present": false,
        "qa_pairs": [],
        "questions": []
      },
      "price": {
        "present": false,
        "raw": "",
        "amount": null,
        "currency": null,
        "source": ""
      }
    },
    "keywords_count": 37
  },
  "seo_analysis": {
    "success": true,
    "analysis": {
      "current_seo": {
        "title_analysis": {
          "content": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
          "keywords_found": [
            "dried strawberries",
            "freeze dried strawberries slices",
            "bulk freeze dried strawberries"
          ],
          "keyword_count": 3,
          "character_count": 199,
          "keyword_density": 1.51,
          "opportunities": [
            "strawberry freeze dried",
            "strawberries freeze dried",
            "dried freeze strawberries",
            "freeze-dried strawberries",
            "freeze dried strawberry"
          ]
        },
        "bullets_analysis": [
          {
            "content": "Delicious Flavor in Every Bite: Savor the naturally sweet, tangy crunch of freeze dried strawberry slices bursting with real fruit flavor. Enjoy Strawberry freeze dried as a fruity boost or add it to oatmeal, yogurt, smoothies, or desserts.",
            "keywords_found": [
              "strawberry freeze dried",
              "freeze dried strawberry",
              "dried strawberry slices",
              "freeze dried strawberry slices"
            ],
            "keyword_count": 4,
            "character_count": 240,
            "keyword_density": 1.67,
            "opportunities": [
              "strawberries freeze dried",
              "dried freeze strawberries",
              "freeze-dried strawberries",
              "freezedried strawberry",
              "freeze dry strawberry"
            ]
          },
          {
            "content": "Ideal Travel Companion: Lightweight, mess-free, and shelf-stable, our freeze dried strawberries bulk are perfect for hiking or camping, backpacking adventures. Enjoy this organic freeze dried fruit straight from the pouch or rehydrate for a fresh fruity treat.",
            "keywords_found": [
              "dried strawberries",
              "freeze dried strawberries bulk"
            ],
            "keyword_count": 2,
            "character_count": 260,
            "keyword_density": 0.77,
            "opportunities": [
              "strawberry freeze dried",
              "strawberries freeze dried",
              "dried freeze strawberries",
              "freeze-dried strawberries",
              "freeze dried strawberry"
            ]
          },
          {
            "content": "From Farm to Your Table: Our organic dried strawberries, delivered sun-ripened, farm-fresh, are made from real strawberries. No added sugar, no preservatives or GMOs - all natural dry strawberries with iron to help support immune health with every bite.",
            "keywords_found": [
              "dried strawberries"
            ],
            "keyword_count": 1,
            "character_count": 253,
            "keyword_density": 0.4,
            "opportunities": [
              "strawberry freeze dried",
              "strawberries freeze dried",
              "dried freeze strawberries",
              "freeze-dried strawberries",
              "freeze dried strawberry"
            ]
          },
          {
            "content": "Shelf Life: Our freeze-dried strawberries are at peak flavor for up to 24 months. For the best taste and texture in every bite, please enjoy within two year of purchase at anywhere at anytime.",
            "keywords_found": [
              "freeze-dried strawberries",
              "dried strawberries"
            ],
            "keyword_count": 2,
            "character_count": 192,
            "keyword_density": 1.04,
            "opportunities": [
              "strawberry freeze dried",
              "strawberries freeze dried",
              "dried freeze strawberries",
              "freeze dried strawberry",
              "freezedried strawberry"
            ]
          },
          {
            "content": "Bulk Packed for Convenience: Buy in bulk and enjoy premium quality freeze dried strawberries whenever you need them. Great for baking, snacking, or mixing with freeze dried fruit for a refreshing fruit combo.",
            "keywords_found": [
              "dried strawberries"
            ],
            "keyword_count": 1,
            "character_count": 208,
            "keyword_density": 0.48,
            "opportunities": [
              "strawberry freeze dried",
              "strawberries freeze dried",
              "dried freeze strawberries",
              "freeze-dried strawberries",
              "freeze dried strawberry"
            ]
          }
        ],
        "backend_keywords": [],
        "keyword_coverage": {
          "total_keywords": 25,
          "covered_keywords": 9,
          "coverage_percentage": 36,
          "missing_high_intent": [
            "strawberries freeze dried",
            "dried freeze strawberries",
            "freezedried strawberry",
            "freeze dry strawberry",
            "freeze dry strawberries",
            "dry strawberry fruit",
            "free dried strawberries",
            "freezer dried strawberries",
            "dried strawberrries",
            "freeze dried strawberries organic"
          ],
          "missing_high_volume": []
        },
        "root_coverage": {
          "total_roots": 7,
          "covered_roots": 0,
          "coverage_percentage": 0,
          "missing_roots": [
            "strawberry",
            "apple",
            "slice",
            "chip",
            "fruit",
            "shortcake",
            "fresa"
          ],
          "root_volumes": {
            "strawberry": 16268,
            "apple": 3235,
            "slice": 2607,
            "chip": 371,
            "fruit": 297,
            "shortcake": 229,
            "fresa": 288
          }
        },
        "total_character_usage": {
          "title_chars": 199,
          "bullets_total_chars": 1153,
          "bullets_avg_chars": 230,
          "backend_chars": 0,
          "total_chars": 1352
        }
      },
      "optimized_seo": {
        "optimized_title": {
          "content": "BREWER Freeze Dried Strawberries Bulk - Organic Strawberry Slices 4 Pack (1.2 oz Each), No Sugar Added, Gluten Free Fruit Snack for Smoothies, Baking & Cereal - Freeze-Dried Strawberries",
          "keywords_included": [
            "freeze dried strawberries bulk",
            "bulk freeze dried strawberries",
            "organic strawberry slices",
            "freeze-dried strawberries",
            "freeze dried strawberry"
          ],
          "improvements": [
            "Front-loaded primary query 'freeze dried strawberries bulk'",
            "Added hyphenated variant 'freeze-dried strawberries' for indexing breadth",
            "Kept under 200 chars while improving readability and benefit language",
            "Included pack size for CTR and relevance"
          ],
          "character_count": 187
        },
        "optimized_bullets": [
          {
            "content": "Crisp, real fruit taste: Freeze dried strawberry slices deliver a sweet, tangy crunch like strawberry chips. Enjoy strawberry freeze dried as a topping for yogurt, oatmeal, cereal, ice cream, or desserts.",
            "keywords_included": [
              "freeze dried strawberry slices",
              "strawberry chips",
              "strawberry freeze dried"
            ],
            "improvements": [
              "Benefit-led lead-in with texture/flavor",
              "Added 'strawberry chips' and exact phrase 'strawberry freeze dried'",
              "Targeted use-case terms for conversion (yogurt, cereal, desserts)"
            ],
            "character_count": 246
          },
          {
            "content": "Clean, organic ingredients: USDA organic, non-GMO, no sugar added or preservatives. Our freeze dried strawberries organic—aka freeze dried organic strawberries—are simply dried strawberries, nothing else. Naturally gluten free.",
            "keywords_included": [
              "freeze dried strawberries organic",
              "freeze dried organic strawberries",
              "dried strawberries"
            ],
            "improvements": [
              "Stacks both order variants for 'organic' phrase coverage",
              "Trust builders (USDA organic, non-GMO, no sugar) to lift CVR",
              "Includes high-volume 'dried strawberries'"
            ],
            "character_count": 260
          },
          {
            "content": "Bulk value & convenience: 4 pack (1.2 oz each) of bulk freeze dried strawberries with resealable pouches; includes freeze dried strawberries slices ready for snacking or toppings. Pantry-friendly and lunchbox-ready.",
            "keywords_included": [
              "bulk freeze dried strawberries",
              "freeze dried strawberries slices"
            ],
            "improvements": [
              "Highlights bulk multi-pack and resealable convenience",
              "Adds exact phrase variant 'freeze dried strawberries slices'",
              "Addresses storage/use cases to reduce objections"
            ],
            "character_count": 245
          },
          {
            "content": "Versatile for baking & blends: Add dried strawberry slices to muffins, shortcake, pancakes, and granola; swirl into smoothies and shakes; rehydrate for sauces or jam. Also great as dehydrated strawberry slices for trail mix and parfaits. Great dry strawberry fruit for cereal and yogurt.",
            "keywords_included": [
              "dried strawberry slices",
              "dehydrated strawberry slices",
              "dry strawberry fruit"
            ],
            "improvements": [
              "Targets baking and smoothie segments with keyword clusters",
              "Captures 'dehydrated' synonym for broader reach",
              "Multiple culinary applications to expand intent coverage"
            ],
            "character_count": 297
          },
          {
            "content": "Adventure-ready & long shelf life: Lightweight, mess-free strawberries freeze dried with a 24-month shelf life—ideal for hiking, camping, travel, and emergency storage. Premium freeze-dried strawberries you can enjoy anywhere.",
            "keywords_included": [
              "strawberries freeze dried",
              "freeze-dried strawberries"
            ],
            "improvements": [
              "Introduces exact phrase 'strawberries freeze dried'",
              "Reinforces shelf life and portability for outdoor/prepper audiences",
              "Closes with brand-relevant quality claim"
            ],
            "character_count": 256
          }
        ],
        "optimized_backend_keywords": [
          "freezedried strawberry",
          "freezer dried strawberries",
          "free dried strawberries",
          "dried freeze strawberries",
          "freeze dry strawberries",
          "freeze dry strawberry",
          "dried strawberrries",
          "dehydrated strawberries sliced",
          "dehydrated strawberries bulk",
          "freeze dried strawberries freeze-dried strawberries slices",
          "fresa"
        ],
        "keyword_strategy": {
          "primary_roots": [
            "strawberry",
            "slice",
            "fruit",
            "chip"
          ],
          "priority_clusters": [
            "freeze dried strawberries bulk",
            "freeze dried strawberry slices",
            "organic/no sugar added/gluten free",
            "use cases: smoothies baking cereal yogurt travel"
          ],
          "phrase_variants_in_frontend": [
            "freeze-dried strawberries",
            "freeze dried strawberry slices",
            "freeze dried strawberries slices",
            "strawberries freeze dried",
            "freeze dried strawberries organic",
            "freeze dried organic strawberries",
            "bulk freeze dried strawberries"
          ],
          "misspellings_and_synonyms_in_backend": [
            "freezedried strawberry",
            "freezer dried strawberries",
            "free dried strawberries",
            "dried strawberrries",
            "freeze dry strawberries",
            "dehydrated strawberries sliced",
            "dehydrated strawberries bulk"
          ],
          "exclusions": [
            "freeze dried apples",
            "freeze dried apple slices",
            "competitor brand terms"
          ]
        },
        "rationale": "Title is front-loaded with the highest-intent, high-volume query ('freeze dried strawberries bulk') and reinforced with the hyphenated variant. Bullets are structured by benefit theme and include exact-match phrases to capture multiple high-intent variants without sacrificing readability. Backend search terms consolidate misspellings, alternate word orders, and 'dehydrated' synonyms not present in front-end content to maximize indexing within the character budget while adhering to Amazon policy (no competitor brands, no commas)."
      },
      "comparison": {
        "coverage_improvement": {
          "total_keywords": 25,
          "before_covered": 9,
          "after_covered": 25,
          "before_coverage_pct": 36,
          "after_coverage_pct": 100,
          "delta_pct_points": 64,
          "new_keywords_added": [
            "dehydrated strawberries bulk",
            "dehydrated strawberries sliced",
            "dehydrated strawberry slices",
            "dried freeze strawberries",
            "dried strawberrries",
            "dry strawberry fruit",
            "free dried strawberries",
            "freeze dried organic strawberries",
            "freeze dried strawberries freeze-dried strawberries slices",
            "freeze dried strawberries organic",
            "freeze dry strawberries",
            "freeze dry strawberry",
            "freezedried strawberry",
            "freezer dried strawberries",
            "strawberries freeze dried",
            "strawberry chips"
          ]
        },
        "intent_improvement": {
          "high_intent_total": 29,
          "before_covered": 9,
          "after_covered": 25,
          "delta": 16
        },
        "volume_improvement": {
          "estimated_volume_before": 13218,
          "estimated_volume_after": 17387,
          "delta_volume": 4169
        },
        "character_efficiency": {
          "title_limit": 200,
          "title_before": 199,
          "title_after": 186,
          "title_utilization_before_pct": 99.5,
          "title_utilization_after_pct": 93,
          "backend_limit": 249,
          "backend_before": 0,
          "backend_after": 290
        },
        "summary_metrics": {
          "overall_improvement_score": 10,
          "priority_recommendations": 4
        }
      },
      "product_context": {
        "title": "BREWER Bulk Freeze Dried Strawberries Slices - Pack of 4 (1.2 Oz Each) Organic Freeze Dried Strawberries No Sugar Added, Dry Strawberry Gluten Free Fruit Snack for Baking, Smoothies, Cereals & Travel",
        "brand": "Brewer Outdoor Solutions",
        "category": "Unknown"
      },
      "analysis_metadata": {
        "total_keywords_analyzed": 37,
        "relevant_keywords_count": 13,
        "high_intent_keywords_count": 29,
        "optimization_method": "ai"
      }
    },
    "summary": {
      "current_coverage": "36.0%",
      "optimization_opportunities": 10,
      "method": "ai"
    }
  },
  "source": "test_research_keywords_seo_endpoint"
};

const Section = ({ title, children, isExpandable = false }: { 
  title: string; 
  children: React.ReactNode; 
  isExpandable?: boolean;
}) => {
  const [isExpanded, setIsExpanded] = useState(!isExpandable);
  
  return (
    <Card className="mb-6">
      <CardHeader 
        className={isExpandable ? "cursor-pointer hover:bg-gray-50" : ""}
        onClick={() => isExpandable && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {title}
          </CardTitle>
          {isExpandable && (
            isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />
          )}
        </div>
      </CardHeader>
      {isExpanded && <CardContent>{children}</CardContent>}
    </Card>
  );
};

const KeyValue = ({ label, value }: { label: string; value: string | number }) => (
  <div className="flex justify-between items-start py-1 border-b border-gray-100 last:border-b-0">
    <span className="font-medium text-gray-600 text-sm">{label}:</span>
    <span className="text-sm text-gray-900 text-right max-w-xs">
      {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
    </span>
  </div>
);

const getCategoryColor = (category: string) => {
  const colors: { [key: string]: string } = {
    'Relevant': 'bg-green-100 text-green-800',
    'Design-Specific': 'bg-blue-100 text-blue-800',
    'Irrelevant': 'bg-red-100 text-red-800',
    'Branded': 'bg-purple-100 text-purple-800',
    'Spanish': 'bg-yellow-100 text-yellow-800',
    'Outlier': 'bg-gray-100 text-gray-800'
  };
  return colors[category] || 'bg-gray-100 text-gray-800';
};

const getIntentBadge = (score: number) => {
  if (score === 0) return <Badge variant="destructive">Intent: 0</Badge>;
  if (score === 1) return <Badge variant="secondary">Intent: 1</Badge>;
  if (score === 2) return <Badge variant="outline">Intent: 2</Badge>;
  if (score === 3) return <Badge className="bg-green-600 text-white">Intent: 3</Badge>;
  return <Badge>Intent: {score}</Badge>;
};

const TestResultsPage = () => {
  const { asin, marketplace, ai_analysis_keywords, seo_analysis, source } = response;
  const { structured_data, final_output, scraped_product } = ai_analysis_keywords;
  const { product_context, items, stats } = structured_data;
  const { analysis } = seo_analysis;
  const { current_seo, optimized_seo, comparison, analysis_metadata } = analysis;

  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Amazon SEO Analysis Results</h1>
              <p className="text-gray-600 mt-1">
                ASIN: <a href={asin} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
                  {asin.replace('http://amazon.com/dp/', '')}
                </a> • {marketplace} Marketplace
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 mb-2">
                <Star className="h-4 w-4 text-yellow-500 fill-current" />
                <span className="font-semibold">4.4 out of 5 stars</span>
              </div>
              <div className="text-sm text-gray-600">93 ratings</div>
            </div>
          </div>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-blue-600 font-semibold">Total Keywords</div>
              <div className="text-2xl font-bold">{items.length}</div>
              <div className="text-sm text-blue-600">Analyzed</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-green-600 font-semibold">Coverage Improvement</div>
              <div className="text-2xl font-bold">+{comparison.coverage_improvement.delta_pct_points}%</div>
              <div className="text-sm text-green-600">{comparison.coverage_improvement.before_coverage_pct}% → {comparison.coverage_improvement.after_coverage_pct}%</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-purple-600 font-semibold">Volume Increase</div>
              <div className="text-2xl font-bold">+{comparison.volume_improvement.delta_volume.toLocaleString()}</div>
              <div className="text-sm text-purple-600">Search Volume</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-orange-600 font-semibold">Optimization Score</div>
              <div className="text-2xl font-bold">{comparison.summary_metrics.overall_improvement_score}/10</div>
              <div className="text-sm text-orange-600">Perfect Score</div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap gap-3">
            <Button
              variant={activeTab === 'overview' ? 'default' : 'outline'}
              onClick={() => setActiveTab('overview')}
              className="flex items-center gap-2"
            >
              <Package size={16} />
              Overview
            </Button>
            <Button
              variant={activeTab === 'keywords' ? 'default' : 'outline'}
              onClick={() => setActiveTab('keywords')}
              className="flex items-center gap-2"
            >
              <Search size={16} />
              Keywords
            </Button>
            <Button
              variant={activeTab === 'seo' ? 'default' : 'outline'}
              onClick={() => setActiveTab('seo')}
              className="flex items-center gap-2"
            >
              <TrendingUp size={16} />
              SEO Analysis
            </Button>
            <Button
              variant={activeTab === 'product' ? 'default' : 'outline'}
              onClick={() => setActiveTab('product')}
              className="flex items-center gap-2"
            >
              <Target size={16} />
              Product Details
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <Section title="Product Information">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <KeyValue label="Title" value={product_context.title} />
                <KeyValue label="Brand" value={product_context.brand} />
                <KeyValue label="Form" value={product_context.form} />
                <KeyValue label="Pack Size" value={product_context.pack_size} />
                <KeyValue label="Unit Size" value={product_context.unit_size_each_oz} />
              </div>
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-gray-600 text-sm">Attributes:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {product_context.attributes.map((attr: string, i: number) => (
                      <Badge key={i} variant="outline">{attr}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="font-medium text-gray-600 text-sm">Use Cases:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {product_context.use_cases.map((use: string, i: number) => (
                      <Badge key={i} variant="secondary">{use}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </Section>

          <Section title="Product Images">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-2">Main Image</h4>
                <Image 
                  src={scraped_product.images.main_image} 
                  alt="Main Product Image" 
                  width={300} 
                  height={300} 
                  className="rounded-lg object-cover border" 
                />
              </div>
              <div>
                <h4 className="font-medium mb-2">All Images ({scraped_product.images.image_count} total)</h4>
                <div className="grid grid-cols-3 gap-2">
                  {scraped_product.images.all_images.slice(0, 6).map((img: string, i: number) => (
                    <Image 
                      key={i} 
                      src={img} 
                      alt={`Product image ${i + 1}`} 
                      width={96} 
                      height={96} 
                      className="w-24 h-24 object-cover rounded border" 
                    />
                  ))}
                </div>
              </div>
            </div>
          </Section>

          <Section title="Category Distribution">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(stats).map(([category, data]: [string, { count: number; examples: string[] }]) => (
                <div key={category} className="text-center p-4 bg-white rounded-lg border">
                  <div className="text-2xl font-bold text-gray-900">{data.count}</div>
                  <div className={`text-sm px-2 py-1 rounded-full mt-1 ${getCategoryColor(category)}`}>
                    {category}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        </div>
      )}

      {/* Keywords Tab */}
      {activeTab === 'keywords' && (
        <div className="space-y-6">
          <Section title="Keyword Analysis">
            <div className="overflow-x-auto">
              <table className="w-full table-auto">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium">Keyword</th>
                    <th className="text-right py-3 px-4 font-medium">Volume</th>
                    <th className="text-center py-3 px-4 font-medium">Intent</th>
                    <th className="text-center py-3 px-4 font-medium">Relevancy</th>
                    <th className="text-right py-3 px-4 font-medium">Title Density</th>
                    <th className="text-center py-3 px-4 font-medium">Category</th>
                    <th className="text-center py-3 px-4 font-medium">Root</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((kw: { 
                    phrase: string; 
                    search_volume: number; 
                    intent_score: number; 
                    relevancy_score: number; 
                    title_density: number; 
                    category: string; 
                    root: string; 
                  }, i: number) => (
                    <tr key={i} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-sm">{kw.phrase}</td>
                      <td className="text-right py-3 px-4 text-sm">{kw.search_volume.toLocaleString()}</td>
                      <td className="text-center py-3 px-4">{getIntentBadge(kw.intent_score)}</td>
                      <td className="text-center py-3 px-4">
                        <Badge variant="outline">{kw.relevancy_score}/10</Badge>
                      </td>
                      <td className="text-right py-3 px-4 text-sm">{kw.title_density}</td>
                      <td className="text-center py-3 px-4">
                        <Badge className={getCategoryColor(kw.category)}>{kw.category}</Badge>
                      </td>
                      <td className="text-center py-3 px-4">
                        <Badge variant="secondary">{kw.root}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        </div>
      )}

      {/* SEO Tab */}
      {activeTab === 'seo' && (
        <div className="space-y-6">
          <Section title="Title Optimization">
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Current Title ({current_seo.title_analysis.character_count} chars)</h4>
                <div className="bg-red-50 p-3 rounded border text-sm border-red-200">
                  {current_seo.title_analysis.content}
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  Keywords found: {current_seo.title_analysis.keywords_found.join(', ')}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Optimized Title ({optimized_seo.optimized_title.character_count} chars)</h4>
                <div className="bg-green-50 p-3 rounded border text-sm border-green-200">
                  {optimized_seo.optimized_title.content}
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  Keywords included: {optimized_seo.optimized_title.keywords_included.join(', ')}
                </div>
              </div>
            </div>
          </Section>

          <Section title="Bullet Point Analysis">
            <div className="space-y-6">
              {current_seo.bullets_analysis.map((bullet: {
                content: string;
                keywords_found: string[];
                opportunities: string[];
                keyword_count: number;
                character_count: number;
                keyword_density: number;
              }, i: number) => (
                <div key={i} className="border rounded-lg p-4">
                  <h5 className="font-medium text-gray-700 mb-2">Bullet Point {i + 1}</h5>
                  <div className="bg-gray-50 p-3 rounded text-sm mb-3">
                    {bullet.content}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <strong>Keywords Found:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {bullet.keywords_found.map((kw: string, j: number) => (
                          <Badge key={j} variant="outline" className="text-xs">{kw}</Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <strong>Opportunities:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {bullet.opportunities.map((op: string, j: number) => (
                          <Badge key={j} variant="secondary" className="text-xs">{op}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-4 mt-3 text-xs text-gray-600">
                    <span>Keywords: {bullet.keyword_count}</span>
                    <span>Characters: {bullet.character_count}</span>
                    <span>Density: {bullet.keyword_density}%</span>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Optimized Bullet Points">
            <div className="space-y-6">
              {optimized_seo.optimized_bullets.map((bullet: {
                content: string;
                keywords_included: string[];
                improvements: string[];
                character_count: number;
              }, i: number) => (
                <div key={i} className="border rounded-lg p-4 bg-green-50 border-green-200">
                  <h5 className="font-medium text-green-700 mb-2">Optimized Bullet Point {i + 1}</h5>
                  <div className="bg-white p-3 rounded text-sm mb-3 border">
                    {bullet.content}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <strong>Keywords Included:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {bullet.keywords_included.map((kw: string, j: number) => (
                          <Badge key={j} className="bg-green-600 text-white text-xs">{kw}</Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <strong>Improvements:</strong>
                      <ul className="list-disc list-inside mt-1 text-xs text-gray-600">
                        {bullet.improvements.map((imp: string, j: number) => (
                          <li key={j}>{imp}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="flex gap-4 mt-3 text-xs text-gray-600">
                    <span>Characters: {bullet.character_count}</span>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          <Section title="SEO Metrics Comparison">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-red-50 p-4 rounded-lg">
                <h4 className="font-medium text-red-600 mb-3">Current SEO</h4>
                <div className="space-y-2">
                  <KeyValue label="Coverage" value={`${comparison.coverage_improvement.before_coverage_pct}%`} />
                  <KeyValue label="Keywords Covered" value={comparison.coverage_improvement.before_covered} />
                  <KeyValue label="Total Keywords" value={comparison.coverage_improvement.total_keywords} />
                </div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-green-600 mb-3">Optimized SEO</h4>
                <div className="space-y-2">
                  <KeyValue label="Coverage" value={`${comparison.coverage_improvement.after_coverage_pct}%`} />
                  <KeyValue label="Keywords Covered" value={comparison.coverage_improvement.after_covered} />
                  <KeyValue label="Volume Increase" value={`+${comparison.volume_improvement.delta_volume.toLocaleString()}`} />
                </div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-600 mb-3">Improvement</h4>
                <div className="space-y-2">
                  <KeyValue label="Coverage Gain" value={`+${comparison.coverage_improvement.delta_pct_points}%`} />
                  <KeyValue label="Intent Improvement" value={`+${comparison.intent_improvement.delta}`} />
                  <KeyValue label="Overall Score" value={`${comparison.summary_metrics.overall_improvement_score}/10`} />
                </div>
              </div>
            </div>
          </Section>

          <Section title="Backend Keywords Strategy">
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Recommended backend search terms to capture misspellings, synonyms, and alternate word orders:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {optimized_seo.optimized_backend_keywords.map((term: string, i: number) => (
                  <Badge key={i} variant="outline" className="text-xs">{term}</Badge>
                ))}
              </div>
            </div>
          </Section>

          <Section title="Root Coverage Analysis" isExpandable>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-red-50 rounded-lg">
                  <h4 className="font-medium text-red-600 mb-2">Current Coverage</h4>
                  <div className="text-2xl font-bold text-red-600">{current_seo.root_coverage.coverage_percentage}%</div>
                  <div className="text-sm text-red-600">{current_seo.root_coverage.covered_roots} of {current_seo.root_coverage.total_roots} roots covered</div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-600 mb-2">Root Volumes</h4>
                  <div className="space-y-1 text-sm">
                    {Object.entries(current_seo.root_coverage.root_volumes).map(([root, volume]: [string, number]) => (
                      <div key={root} className="flex justify-between">
                        <span>{root}:</span>
                        <span className="font-medium">{volume.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </Section>

          <Section title="Character Usage Analysis" isExpandable>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2">Title Usage</h4>
                <div className="text-2xl font-bold">{current_seo.total_character_usage.title_chars}</div>
                <div className="text-sm text-gray-600">characters used</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2">Bullets Total</h4>
                <div className="text-2xl font-bold">{current_seo.total_character_usage.bullets_total_chars}</div>
                <div className="text-sm text-gray-600">avg: {current_seo.total_character_usage.bullets_avg_chars} chars</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2">Backend Usage</h4>
                <div className="text-2xl font-bold">{current_seo.total_character_usage.backend_chars}</div>
                <div className="text-sm text-gray-600">characters used</div>
              </div>
            </div>
          </Section>

          <Section title="Keyword Strategy Details" isExpandable>
            <div className="space-y-6">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Primary Roots</h4>
                <div className="flex flex-wrap gap-2">
                  {optimized_seo.keyword_strategy.primary_roots.map((root: string, i: number) => (
                    <Badge key={i} className="bg-blue-600 text-white">{root}</Badge>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Priority Clusters</h4>
                <div className="space-y-2">
                  {optimized_seo.keyword_strategy.priority_clusters.map((cluster: string, i: number) => (
                    <div key={i} className="p-2 bg-blue-50 rounded text-sm">{cluster}</div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-700 mb-2">Frontend Phrase Variants</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {optimized_seo.keyword_strategy.phrase_variants_in_frontend.map((phrase: string, i: number) => (
                    <Badge key={i} variant="outline" className="text-xs">{phrase}</Badge>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-700 mb-2">Backend Misspellings & Synonyms</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {optimized_seo.keyword_strategy.misspellings_and_synonyms_in_backend.map((term: string, i: number) => (
                    <Badge key={i} variant="secondary" className="text-xs">{term}</Badge>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-700 mb-2">Exclusions</h4>
                <div className="flex flex-wrap gap-2">
                  {optimized_seo.keyword_strategy.exclusions.map((exclusion: string, i: number) => (
                    <Badge key={i} variant="destructive" className="text-xs">{exclusion}</Badge>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2">Rationale</h4>
                <p className="text-sm text-gray-600">{optimized_seo.rationale}</p>
              </div>
            </div>
          </Section>
        </div>
      )}

      {/* Product Details Tab */}
      {activeTab === 'product' && (
        <div className="space-y-6">
          <Section title="Product Details" isExpandable>
            <div className="space-y-4">
              {Object.entries(scraped_product.elements.detailBullets_feature_div.kv).map(([key, value]) => (
                <KeyValue key={key} label={key} value={value} />
              ))}
            </div>
          </Section>

          <Section title="Feature Bullets" isExpandable>
            <div className="space-y-3">
              {scraped_product.elements["feature-bullets"].bullets.map((bullet: string, i: number) => (
                <div key={i} className="p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                  <div className="text-sm">{bullet}</div>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Customer Reviews" isExpandable>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-500 fill-current" />
                  <span className="font-semibold text-lg">4.4 out of 5 stars</span>
                </div>
                <span className="text-gray-600">93 ratings</span>
              </div>
              
              <div className="space-y-3">
                {scraped_product.reviews.sample_reviews.map((review: string, i: number) => (
                  <div key={i} className="p-4 bg-gray-50 rounded-lg border">
                    <p className="text-sm text-gray-700 italic">&quot;{review}&quot;</p>
                  </div>
                ))}
              </div>
            </div>
          </Section>

          <Section title="Analysis Metadata" isExpandable>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(analysis_metadata).map(([key, value]) => (
                <KeyValue key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={value} />
              ))}
            </div>
          </Section>
        </div>
      )}

      {/* Footer */}
      <Card className="mt-8">
        <CardContent className="p-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div>
              <strong>Final Output:</strong> {final_output}
            </div>
            <div>
              <strong>Source:</strong> {source}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TestResultsPage;

from elasticsearch import Elasticsearch
import json
import nltk.data


def advanced_query(query):
    dis_max = {
        "query": {
            "dis_max": {
                "queries": [
                    {"match": {"title": query}},
                    {"match": {"body": query}}
                ],
                "tie_breaker": 0.3
            }
        },
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-datehistogram-aggregation.html
        "aggregations": {
            "ArticleDates": {
                "date_histogram": {
                    "field": "date",
                    "interval": "1y",
                    "format": "yyyy-MM-dd"
                }
            }
        }
    }
    return dis_max


def summarise(query, text):
    tokenizer = nltk.data.load("nltk:tokenizers/punkt/dutch.pickle")
    summarisation = ""
    for sentence in tokenizer.tokenize(text):
        if any([word in sentence for word in query.split()]):
            print sentence.encode("utf-8"), word
            sentence = sentence.replace(
                word, "<b>{}</b>".format(word).encode("utf-8"))
            summarisation += sentence + " "
        if len(summarisation.split()) > 50:
            break

    if (len(summarisation) < 1):
        return " ".join(text.strip().split()[:50])
    else:
        return summarisation.strip()


def advanced_search(query):
    es = Elasticsearch()

    es.indices.refresh(index="telegraaf")

    res = es.search(index="telegraaf", body=advanced_query(query))
    for hit in res["hits"]["hits"]:
        hit["_source"]["text"] = summarise(query, hit["_source"]["text"])
    # print "Total results: {}!".format(results["hits"]["total"])
    # print "Showing top 5 results!\n"
    # for hit in results["hits"]["hits"][:5]:
    #     print "{} - {} - {}".format(hit["_score"], hit["_source"]["subject"], hit["_source"]["date"])
    #     print hit["_source"]["source"]
    #     print hit["_source"]["title"].encode("utf-8"), "\n"

    barStats = ""
    for dd in res["aggregations"]["ArticleDates"]["buckets"]:
        yr = dd['key_as_string'].split('-', 1)[0]
        dc = dd['doc_count']
        barStats += yr + '-' + str(dc) + '/'

    return res, barStats

if __name__ == '__main__':
    simple_search("oorlog in duitsland")
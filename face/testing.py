


from wikiapi import WikiApi
wiki = WikiApi()
x = wiki.get_article(wiki.find("islamabad")[0]).summary


print("\n\n\n")
print(len(x))
print("\n\n\n")
print(x[:500])
print("\n\n\n")


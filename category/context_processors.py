from .models import Category

# コンテキストプロセッサーを使うことでviewsで指定することなくデフォルトでtemplateに組み込むことができる


def menu_request(request):
    links = Category.objects.all()
    return dict(links=links)

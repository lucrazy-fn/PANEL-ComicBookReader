"""Ponto de entrada oficial do aplicativo desktop."""

def main() -> None:
    # Import tardio: mensagens de dependência e inicialização visual continuam
    # pertencendo ao módulo da interface durante a migração gradual.
    from ComicReader import LibraryWindow

    app = LibraryWindow()
    app.mainloop()

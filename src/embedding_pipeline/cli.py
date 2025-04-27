import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.style import Style
from dotenv import load_dotenv
from src.embedding_pipeline.schema import Document
from src.embedding_pipeline.service import EmbeddingPipelineService
from src.embedding_pipeline.embedding import CohereEmbeddingModel
from src.embedding_pipeline.repository import DocumentRepository
from src.embedding_pipeline.exceptions import InsertDocumentException

load_dotenv()


@click.command("verify-documents", help="Verify all json documents in a folder to ensure they are valid.")
@click.option("--folder", "-f", help="Path to the folder containing documents.")
@click.option("--verbose", "-v", is_flag=True, help="Show invalid documents as a list.")
def verify_documents(folder: str, verbose: bool = False):
    valid_docs, invalid_doc_content, non_json_files = asyncio.run(EmbeddingPipelineService.load_documents_from_folder(folder))
    tot_valid_docs = len(valid_docs)
    tot_invalid_doc_contents = len(invalid_doc_content)
    tot_non_json_files = len(non_json_files)

    table = Table(title="Folder Verification Results", show_lines=True)
    table.add_column("Description", style="magenta")
    table.add_column("Results", justify="right", style="green")
    table.add_row("Folder", f"{folder}")
    table.add_row("Total Valid Documents", f"{tot_valid_docs}")
    table.add_row("Total Invalid Document Content", f"{tot_invalid_doc_contents}")
    table.add_row("Total Non Json Files", f"{tot_non_json_files}")

    console = Console()
    console.print(table)

    if verbose:
        console.print("\n\n")
        console.rule("[bold red]Invalid json document content[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, invalid_doc in enumerate(invalid_doc_content):
            console.print(f"\t{i+1}: {invalid_doc}", style="red")
        console.print("\n")

        console.rule("[bold red]Non json files[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, non_json_doc in enumerate(non_json_files):
            console.print(f"\t{i+1}: {non_json_doc}", style="red")


async def _insert_document(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 50) -> list[str]:
    """
    Load a document and process it by splitting its pages into text chunks and embedding them.
    """
    embedding_model = await CohereEmbeddingModel.create()
    repository =  DocumentRepository()
    document_insert_error = []
    for document in documents:
        try:
            await EmbeddingPipelineService.save_document_into_db(document, embedding_model, repository, chunk_size, chunk_overlap)
        except InsertDocumentException:
            document_insert_error += [document.doc_name]

    return document_insert_error


@click.command("load-documents", help="Verify all json documents in a folder to ensure they are valid.")
@click.option("--folder", "-f", help="Path to the folder containing documents.")
@click.option("--chunk-size", "-cs", help="Path to the folder containing documents.", type=click.INT)
@click.option("--chunk-overlap", "-co", help="Path to the folder containing documents.", type=click.INT)
@click.option("--verbose", "-v", is_flag=True, help="Show invalid documents as a list.")
def load_documents(folder: str, chunk_size: int, chunk_overlap: int, verbose: bool = False):
    """
    Loads all files from a folder and its subfolders into a list of strings.
    """
    valid_docs, invalid_doc_content, non_json_files = asyncio.run(EmbeddingPipelineService.load_documents_from_folder(folder))
    list_not_inserted_documents = asyncio.run(_insert_document(valid_docs, chunk_size, chunk_overlap))

    tot_valid_docs = len(valid_docs)
    tot_invalid_doc_contents = len(invalid_doc_content)
    tot_non_json_files = len(non_json_files)
    tot_not_inserted_documents = len(list_not_inserted_documents)
    tot_inserted_documents = tot_valid_docs - tot_not_inserted_documents

    table = Table(title="Insert Documents Results", show_lines=True)
    table.add_column("Description", style="magenta")
    table.add_column("Results", justify="right", style="green")
    table.add_row("Folder", f"{folder}")
    table.add_row("Total Valid Documents", f"{tot_valid_docs}")
    table.add_row("Total Invalid Document Content", f"{tot_invalid_doc_contents}")
    table.add_row("Total Non Json Files", f"{tot_non_json_files}")
    table.add_row("Total Inserted Documents", f"{tot_inserted_documents}")
    table.add_row("Total Not Inserted Documents", f"{tot_not_inserted_documents}")

    console = Console()
    console.print(table)
    if verbose:
        console.print("\n\n")
        console.rule("[bold red]Invalid json document content[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, invalid_doc in enumerate(invalid_doc_content):
            console.print(f"\t{i+1}: {invalid_doc}", style="red")

        console.rule("[bold red]Non json files[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, non_json_doc in enumerate(non_json_files):
            console.print(f"\t{i+1}: {non_json_doc}", style="red")

        console.rule("[bold red]Non Inserted Documents[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, non_inserted in enumerate(list_not_inserted_documents):
            console.print(f"\t{i+1}: {non_inserted}", style="red")


@click.command("remove-documents-from-db", help="Remove from database documents in a folder.")
@click.option("--folder", "-f", help="Path to the folder containing documents.")
@click.option("--verbose", "-v", is_flag=True, help="Show invalid documents as a list.")
def remove_documents_from_db(folder:str, verbose: bool = False):
    """
    Removes a document from the database.
    """
    loop = asyncio.get_event_loop()


    valid_docs, invalid_doc_content, non_json_files = loop.run_until_complete(EmbeddingPipelineService.load_documents_from_folder(folder))
    tot_valid_docs = len(valid_docs)
    tot_invalid_doc_contents = len(invalid_doc_content)
    tot_non_json_files = len(non_json_files)

    repository = DocumentRepository()
    non_deleted_documents = loop.run_until_complete(EmbeddingPipelineService.delete_documents(valid_docs, repository))

    tot_non_deleted_documents = len(non_deleted_documents) 
    tot_inserted_documents = tot_valid_docs - tot_non_deleted_documents


    table = Table(title="Insert Documents Results", show_lines=True)
    table.add_column("Description", style="magenta")
    table.add_column("Results", justify="right", style="green")
    table.add_row("Folder", f"{folder}")
    table.add_row("Total Valid Documents", f"{tot_valid_docs}")
    table.add_row("Total Invalid Document Content", f"{tot_invalid_doc_contents}")
    table.add_row("Total Non Json Files", f"{tot_non_json_files}")
    table.add_row("Total Deleted Documents", f"{tot_inserted_documents}")
    table.add_row("Total Non Deleted Documents", f"{tot_non_deleted_documents}")
    
    console = Console()
    console.print(table)
    if verbose:
        console.print("\n\n")
        console.rule("[bold red]Invalid json document content[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, invalid_doc in enumerate(invalid_doc_content):
            console.print(f"\t{i+1}: {invalid_doc}", style="red")

        console.rule("[bold red]Non json files[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, non_json_doc in enumerate(non_json_files):
            console.print(f"\t{i+1}: {non_json_doc}", style="red")

        console.rule("[bold red]Non Deleted Documents[/bold red] [red] ", align="left", style=Style(color="red1"))
        for i, non_deleted in enumerate(non_deleted_documents):
            console.print(f"\t{i+1}: {non_deleted}", style="red")



# Grupo principal que agrega todos os commands
@click.group()
def cli():
    """CLI com comandos síncronos e assíncronos"""
    pass


cli.add_command(verify_documents)
cli.add_command(load_documents)
cli.add_command(remove_documents_from_db)


if __name__ == "__main__":
    cli()

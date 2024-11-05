import pymupdf
import os
from typing import Union, List, Optional
from PIL import Image, ImageTk


class Page:
    page_id = 0

    def __init__(self, page: pymupdf.Page, pdf_file_id: int, preview_image: Optional[Image] = None):
        self.obj = page
        self.pdf_id = pdf_file_id
        self.original_index = page.number

        # Add Page ID
        self.id = Page.page_id
        Page.page_id += 1


class StructureElement:
    element_id = 0

    def __init__(self, page_objects: Union[Page, List[Page]]):

        self.page_objects = page_objects if isinstance(page_objects, list) else [page_objects]
        self.num_pages = len(self.page_objects)

        # Add element ID
        self.id = StructureElement.element_id
        StructureElement.element_id += 1

        # Collaped state determines if multiple pages are in the element
        self.collapsed = self.num_pages > 1

        self.excluded = False  # If excluded in export

    """
    def __str__(self):
        return_list = []
        for page in self.page_objects:
            return_list.append(f"PDF{page.pdf_id}-p.{page.original_index}")

        return f"[{', '.join(return_list)}]"
    """

    def __str__(self):
        return f"[{self.id}{':collaped' if self.collapsed else ''}{':excluded' if self.excluded else ''}]"

    def exclude(self, val=True):
        if val:
            self.excluded = True
        else:
            self.excluded = False


class PdfHandler:
    pdf_file_id = 0

    def __init__(self):
        self.loaded_pdfs = {}
        self.structure = []
        self.element_index_map = {}  # Dictionary for fast lookup

    def __str__(self):
        return_str = ""
        for elem in self.structure:
            return_str += str(elem)

        return return_str

    def add_pdf_file(self, file_path, index: Optional[int] = None, collaped_load = True):
        pdf_obj = pymupdf.open(file_path)
        pdf_name = os.path.basename(file_path)
        page_count = pdf_obj.page_count
        pdf_id = PdfHandler.pdf_file_id
        PdfHandler.pdf_file_id += 1

        self.loaded_pdfs[pdf_id] = {"name": pdf_name, "page_count": page_count}

        # Add pdf to element struture
        page_objects = [Page(pdf_file_id=pdf_id, page=page) for page in pdf_obj]
        if collaped_load:
            new_elements = [StructureElement(page_objects=page_objects)]
        else:
            new_elements = [StructureElement(page_objects=page) for page in page_objects]

        # Add elements to index that is specified, if none, add to end
        if not index:
            self.structure.extend(new_elements)
        else:
            self.structure[index:index] = new_elements

        self._update_index_map()  # Update the index map after adding elements

        return new_elements

    def move_element(self, element_id, new_index):
        if element_id in self.element_index_map:
            old_index = self.element_index_map[element_id]
            element = self.structure.pop(old_index)  # Remove the element from the list

            # Insert the element at the new index
            self.structure.insert(new_index, element)

            self._update_index_map()  # Update index map after moving an element

    def expand_element(self, element_id):

        if element_id in self.element_index_map:
            old_index = self.element_index_map[element_id]
            element = self.structure.pop(old_index)  # Remove the element from the list

            # Create new structure element from element pages
            new_elements = []
            for page in element.page_objects:
                new_elements.append(StructureElement(page_objects=page))

            # Add new elements to structure at old colapsed element index
            self.structure[old_index:old_index] = new_elements

        self._update_index_map()
        return new_elements

    def toggle_exclude_element(self, element_id):
        element = self.get_element_by_id(element_id)
        if element.excluded:
            element.exclude(False)
        else:
            element.exclude()

    def collapse_elements(self, element_ids):
        page_objects = []
        old_indexes = []

        # Collect indices and corresponding elements to collapse
        for element_id in element_ids:
            if element_id in self.element_index_map:  # Check if element_id exists
                old_index = self.element_index_map[element_id]
                old_indexes.append(old_index)

                # Get the element before removing it
                element = self.structure[old_index]
                page_objects.extend(element.page_objects)  # Extend because elements can be collapsed themselves

        # Sort indices in descending order for safe removal
        old_indexes.sort(reverse=True)

        # Remove elements from the structure
        for old_index in old_indexes:
            self.structure.pop(old_index)

        # Insert the new collapsed element at the lowest index
        new_element = StructureElement(page_objects=page_objects)
        self.structure.insert(min(old_indexes), new_element)

        # Update index map after modifications
        self._update_index_map()

    def _update_index_map(self):
        self.element_index_map.clear()  # Clear the current index map
        for index, element in enumerate(self.structure):
            self.element_index_map[element.id] = index  # Rebuild the index map

    def get_element_index(self, element_id):
        return self.element_index_map.get(element_id, -1)  # Return -1 if not found

    def get_element_by_id(self, element_id):
        """Retrieve an element from the structure by its ID."""
        if element_id in self.element_index_map:
            index = self.element_index_map[element_id]
            return self.structure[index]
        return None

    def get_structure(self):
        return self.structure


if __name__ == '__main__':
    pdf_handler = PdfHandler()
    pdf_handler.add_pdf_file("files/table.pdf", collaped_load=False)
    pdf_handler.add_pdf_file("files/paper.pdf")
    print(pdf_handler)
    pdf_handler.move_element(2, 1)
    print(pdf_handler)
    pdf_handler.expand_element(2)
    print(pdf_handler)
    pdf_handler.collapse_elements([0, 3, 4, 5, 6])
    print(pdf_handler)
    pdf_handler.expand_element(24)
    print(pdf_handler)
    pdf_handler.toggle_exclude_element(25)
    print(pdf_handler)
    pdf_handler.collapse_elements([21, 22, 23, 1])
    print(pdf_handler)
    pdf_handler.toggle_exclude_element(30)
    print(pdf_handler)
    pdf_handler.add_pdf_file("files/rechnung.pdf", index=16, collaped_load=False)
    print(pdf_handler)

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Any, Optional, Dict, Generator
import random
import re
import csv
from tqdm import tqdm
import os
from pathlib import Path


# Alias for some type hints
dataset_t = List[Dict[str, Any]]
context_t = Dict[str, Any]


class FieldType(Enum):

    """Enumeration of supported field types for dataset generation."""

    CHOICE: auto = auto()
    CHOICE_WEIGHTED: auto = auto()
    RANGE: auto = auto()
    FORMAT: auto = auto()
    INCREMENT: auto = auto()


@dataclass
class FieldSpec:

    """Specification for a single field in the dataset."""

    name: str
    field_t: FieldType
    values: Optional[List[Any]] = None
    minr: Optional[int] = None
    maxr: Optional[int] = None
    fmt: Optional[str] = None
    weights: Optional[List[float]] = None
    step: Optional[int] = 1


@dataclass
class Template:

    """Template for generating a dataset."""

    fields: List[FieldSpec]
    current: int = 0  # not sure we should do this like that, but whatever this is some random python code



class DatasetGenerator:

    """Static class that can create datasets based on provided templates."""

    @staticmethod
    def _verify_field(f: FieldSpec) -> None:
        
        # mainly useful to debug templates, given that they are wrongly defined
        # overall ugly function, sorry about that

        match f.field_t:

            case FieldType.CHOICE:
                if not f.values:
                    raise ValueError(f"Field {f.name} of type CHOICE must have a non-empty values list.")
                
            case FieldType.CHOICE_WEIGHTED:
                if not f.values or not f.weights:
                    raise ValueError(f"Field {f.name} of type CHOICE_WEIGHTED must have non-empty values and weights lists.")
                if len(f.values) != len(f.weights):
                    raise ValueError(f"Field {f.name} has mismatched lengths for values and weights.")
                if any(w < 0 for w in f.weights):
                    raise ValueError(f"Field {f.name} has negative weights, which is not allowed.")
                if sum(f.weights) != 1.0:
                    raise ValueError(f"Field {f.name} weights must sum to 1.0.")
                
            case FieldType.RANGE:
                if f.minr is None or f.maxr is None:
                    raise ValueError(f"Field {f.name} of type RANGE must have minr and maxr defined.")
                if f.minr > f.maxr:
                    raise ValueError(f"Field {f.name} has minr greater than maxr.")
        
            case FieldType.FORMAT:
                if not f.fmt:
                    raise ValueError(f"Field {f.name} of type FORMAT must have a fmt string defined.")
                if not re.search(r"\{[^}]+\}", f.fmt): # allow non-empty {...} format strings
                    raise ValueError(f"Field {f.name} has an invalid format string: {f.fmt}")
                
            case FieldType.INCREMENT:
                if f.step is None or f.step <= 0:
                    raise ValueError(f"Field {f.name} of type INCREMENT must have a positive step defined.")
                
            case _:
                raise ValueError(f"Unsupported field type {f.field_t} for field {f.name}.")

    @staticmethod
    def _verify_template(t: Template) -> None:

        # same as above, spams _verify_field over all fields

        if not t.fields: raise ValueError("Template must have at least one field.")
        for f in t.fields: DatasetGenerator._verify_field(f)

    @staticmethod
    def _format_field(f: FieldSpec, ctx: context_t) -> str:

        # use python's built-in string formatting to generate the field value
        # i think this is safe enough, given that the context is controlled

        try: return f.fmt.format(**ctx)
        except KeyError as e: raise ValueError(f"Missing context key {e} for field {f.name} format.") from e

    @staticmethod
    def _weighted_choice(choices: List[Any], weights: List[float]) -> Any:

        # simple weighted random choice implementation
        # do you actually believe that I needed to check on the internet how to do this?
        # "smart" they say rotfl

        total: float = sum(weights)
        rnd: float = random.uniform(0, total)
        cumulative: float = 0

        for choice, weight in zip(choices, weights):
            cumulative += weight
            if rnd < cumulative:
                return choice
            
        return choices[-1]  # fallback, should not happen

    @staticmethod
    def _increment_field(f: FieldSpec, ctx: context_t) -> int:

        # poorly implemented increment field generator
        # could be improved, but whatever

        current: int = ctx.get('CURRENT', 0)
        ctx['CURRENT'] = current + f.step
        return current

    @staticmethod
    def _generate_field(f: FieldSpec, ctx: context_t) -> Any:

        # this one is pretty in my eyes uwu
        # generates a field value based on its type and the provided context

        match f.field_t:
            case FieldType.CHOICE: return random.choice(f.values)
            case FieldType.CHOICE_WEIGHTED: return DatasetGenerator._weighted_choice(f.values, f.weights)
            case FieldType.RANGE: return random.randint(f.minr, f.maxr)
            case FieldType.FORMAT: return DatasetGenerator._format_field(f, ctx)
            case FieldType.INCREMENT: return DatasetGenerator._increment_field(f, ctx)
            case _: raise ValueError(f"Unsupported field type {f.field_t} for field {f.name}.")
    
    @staticmethod
    def choices_from_file(fp: str) -> List[str]:

        """
        Utility function to read choices from a file, one per line. \n
        Raises `FileNotFoundError` if the file does not exist.
        """

        if not os.path.isfile(fp):
            raise FileNotFoundError(f"The file {fp} does not exist.")
        with open(fp, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    @staticmethod
    def generate_dataset(template: Template, records: int) -> dataset_t:

        """
        Generate a dataset based on the provided template and number of records. \n
        This might raise several exceptions if the template is invalid. Please refer to the
        `_verify_template` and `_verify_field` docstrings methods for more details.
        """

        if records <= 0:
            raise ValueError("Number of records must be a positive integer.")

        # validate the template first
        DatasetGenerator._verify_template(template)
        dataset: dataset_t = []
        iterator: Generator[int, None, None] = range(records)
        
        # generate the records using the template
        for _ in tqdm(iterator, desc="[i] Generating dataset", unit="record"):
            rctx: context_t = {'CURRENT': template.current}
            for field in template.fields:
                value: Any = DatasetGenerator._generate_field(field, rctx)
                rctx[field.name] = value
            template.current = rctx['CURRENT']
            _ = rctx.pop('CURRENT', None)
            dataset.append(rctx)
        
        return dataset
    
    @staticmethod
    def export_csv(dataset: dataset_t, filepath: str) -> None:

        """
        Export the provided dataset to a CSV file at the specified filepath. \n
        Raises `ValueError` if the dataset is empty.
        """
        
        if not dataset:
            raise ValueError("Dataset is empty, cannot export to CSV.")
        
        iterator: Generator[int, None, None] = range(len(dataset))
        fieldnames: List[str] = list(dataset[0].keys())

        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer: csv.DictWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in tqdm(iterator, desc="[i] Exporting to CSV", unit="record"):
                writer.writerow(dataset[i])



class CovidDatasetExample:

    """
    Example class to generate a simple `Covid-19` dataset with nodes and relationships. \n
    Nodes represent individuals with a chance of having `Covid-19`, and relationships represent
    interactions between individuals with different exposure levels.
    """

    res_fp: Path = Path(__file__).resolve().parent.parent.parent / r'res'
    
    @staticmethod
    def node_csv(fp: str, covid_odds: float, records: int) -> dataset_t:

        """
        Generate a CSV file with a dataset of individuals, some of whom may have `Covid-19`. \n
        The odds of having `Covid-19` can be adjusted via the `covid_odds` parameter. \n
        Raises `ValueError` if the odds are not between 0 and 1, or if the records count is not positive.
        """

        fnds_fp: str = str(CovidDatasetExample.res_fp / 'fnames')
        lnds_fp: str = str(CovidDatasetExample.res_fp / 'lnames')
        countriesds_fp: str = str(CovidDatasetExample.res_fp / 'countries')
        

        template: Template = Template(fields=[
            FieldSpec(name='id', field_t=FieldType.INCREMENT, step=1),
            FieldSpec(name='first_name', field_t=FieldType.CHOICE, values=DatasetGenerator.choices_from_file(fnds_fp)),
            FieldSpec(name='last_name', field_t=FieldType.CHOICE, values=DatasetGenerator.choices_from_file(lnds_fp)),
            FieldSpec(name='age', field_t=FieldType.RANGE, minr=1, maxr=100),
            FieldSpec(name='has_covid', field_t=FieldType.CHOICE_WEIGHTED, values=[True, False], weights=[covid_odds, 1 - covid_odds]),
            FieldSpec(name='origin', field_t=FieldType.CHOICE, values=DatasetGenerator.choices_from_file(countriesds_fp))
        ])

        # Generate a dataset with some records and export to CSV
        dataset: dataset_t = DatasetGenerator.generate_dataset(template, records)
        DatasetGenerator.export_csv(dataset, fp)
        return dataset

    @staticmethod
    def relationship_csv(fp: str, dataset: dataset_t, max_relationships: int) -> dataset_t:

        """
        Generate a CSV file with a dataset of relationships between individuals in the provided dataset. \n
        Each relationship has an exposure level which can be `CLOSE`, `CASUAL`, or `DISTANT`, as well as a country of origin. \n
        Raises `ValueError` if the provided dataset is empty or if the max_relationships count is not positive.
        """

        if not dataset: raise ValueError("Dataset is empty, cannot generate relationships.")
        if max_relationships <= 0: raise ValueError("Max relationships must be a positive integer.")

        n: int = len(dataset)

        template: Template = Template(fields=[
            FieldSpec(name='id', field_t=FieldType.INCREMENT, step=1),
            FieldSpec(name='from_id', field_t=FieldType.RANGE, minr=0, maxr=n-1),
            FieldSpec(name='to_id', field_t=FieldType.RANGE, minr=0, maxr=n-1),
            FieldSpec(name='exposure', field_t=FieldType.CHOICE, values=['CLOSE', 'CASUAL', 'DISTANT']),
        ])       
        
        # Generate a dataset with some records and export to CSV
        dataset_rel: dataset_t = DatasetGenerator.generate_dataset(template, max_relationships)
        
        DatasetGenerator.export_csv(dataset_rel, fp)
        return dataset_rel



if __name__ == "__main__":
    
    # Covid 19 dataset example. Overall, try to keep the relationship count higher than the node count,
    # otherwise the relationships will be sparse and not very useful for testing.
    # I think a good rule of thumb is to have at least 2-3x more relationships than nodes.

    ...

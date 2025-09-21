
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Any, Optional, Dict, Generator
import random
import re
import csv
from tqdm import tqdm
import os


class FieldType(Enum):
    CHOICE = auto()
    CHOICE_WEIGHTED = auto()
    RANGE = auto()
    FORMAT = auto()


@dataclass
class FieldSpec:
    name: str
    field_t: FieldType
    values: Optional[List[Any]] = None
    minr: Optional[int] = None
    maxr: Optional[int] = None
    fmt: Optional[str] = None
    weights: Optional[List[float]] = None


@dataclass
class Template:
    fields: List[FieldSpec]



class DatasetGenerator:

    @staticmethod
    def _verify_field(f: FieldSpec) -> None:
        
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
                if not re.search(r"\{(\w+)\}", f.fmt):
                    raise ValueError(f"Field {f.name} has an invalid format string: {f.fmt}")
                
            case _:
                raise ValueError(f"Unsupported field type {f.field_t} for field {f.name}.")

    @staticmethod
    def _verify_template(t: Template) -> None:

        if not t.fields:
            raise ValueError("Template must have at least one field.")
        
        for f in t.fields:
            DatasetGenerator._verify_field(f)

    @staticmethod
    def _format_field(f: FieldSpec, ctx: Dict[str, Any]) -> str:
        try:
            return f.fmt.format(**ctx)
        except KeyError as e:
            raise ValueError(f"Missing context key {e} for field {f.name} format.") from e

    @staticmethod
    def _weighted_choice(choices: List[Any], weights: List[float]) -> Any:
        total = sum(weights)
        rnd = random.uniform(0, total)
        cumulative = 0
        for choice, weight in zip(choices, weights):
            cumulative += weight
            if rnd < cumulative:
                return choice
        return choices[-1]  # Fallback

    @staticmethod
    def _generate_field(f: FieldSpec, ctx: Dict[str, Any]) -> Any:
        match f.field_t:
            case FieldType.CHOICE: return random.choice(f.values)
            case FieldType.CHOICE_WEIGHTED: return DatasetGenerator._weighted_choice(f.values, f.weights)
            case FieldType.RANGE: return random.randint(f.minr, f.maxr)
            case FieldType.FORMAT: return DatasetGenerator._format_field(f, ctx)
            case _: raise ValueError(f"Unsupported field type {f.field_t} for field {f.name}.")
    
    @staticmethod
    def choices_from_file(fp: str) -> List[str]:

        if not os.path.isfile(fp):
            raise FileNotFoundError(f"The file {fp} does not exist.")
        
        with open(fp, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    @staticmethod
    def generate_dataset(template: Template, records: int) -> List[Dict[str, Any]]:
        
        # validate the template first
        DatasetGenerator._verify_template(template)
        dataset: List[Dict[str, Any]] = []
        iterator: Generator[int, None, None] = range(records)
        
        # generate the records using the template
        for _ in tqdm(iterator, desc="[i] Generating dataset", unit="record"):
            rctx: Dict[str, Any] = {}
            for field in template.fields:
                value = DatasetGenerator._generate_field(field, rctx)
                rctx[field.name] = value
            dataset.append(rctx)
        
        return dataset
    
    @staticmethod
    def export_csv(dataset: List[Dict[str, Any]], filepath: str) -> None:
        
        if not dataset:
            raise ValueError("Dataset is empty, cannot export to CSV.")
        
        iterator: Generator[int, None, None] = range(len(dataset))
        fieldnames: List[str] = list(dataset[0].keys())

        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer: csv.DictWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in tqdm(iterator, desc="[i] Exporting to CSV", unit="record"):
                writer.writerow(dataset[i])


if __name__ == "__main__":
    
    # Covid 19 dataset example
    template: Template = Template(fields=[
        FieldSpec(name='first_name', field_t=FieldType.CHOICE, values=DatasetGenerator.choices_from_file('res/fnames')),
        FieldSpec(name='last_name', field_t=FieldType.CHOICE, values=DatasetGenerator.choices_from_file('res/lnames')),
        FieldSpec(name='age', field_t=FieldType.RANGE, minr=1, maxr=100),
        FieldSpec(name='country', field_t=FieldType.CHOICE, values=DatasetGenerator.choices_from_file('res/countries')),
        FieldSpec(name='has_covid', field_t=FieldType.CHOICE_WEIGHTED, values=[True, False], weights=[0.1, 0.9]),
    ])

    # Generate a dataset with 1,000,000 records and export to CSV
    dataset: List[Dict[str, Any]] = DatasetGenerator.generate_dataset(template, records=1_000_000)
    DatasetGenerator.export_csv(dataset, filepath='res/covid_dataset_test.csv')


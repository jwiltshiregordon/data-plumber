import ast
import csv
import importlib
import inspect
import json
import keyword
from collections import Counter, defaultdict
from dataclasses import asdict
from functools import wraps
from itertools import combinations
from jinja2 import Template

import journal


def reload_journal():
    importlib.invalidate_caches()
    importlib.reload(journal)


def get_return_type(function_reference):
    annotation = inspect.signature(function_reference).return_annotation
    return_type_code = None
    try:
        return_type_code = inspect.getsource(annotation)
    except Exception:
        pass
    return_type_name = "str"
    if str(annotation).startswith("typing."):
        return_type_name = str(annotation)[len("typing."):], return_type_code
    elif hasattr(annotation, "__name__"):
        return_type_name = annotation.__name__

    return return_type_name, return_type_code


def remove_plumber_decorator(source_code):
    module = ast.parse(source_code)
    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef):
            node.decorator_list = [
                decorator for decorator in node.decorator_list
                if not isinstance(decorator, ast.Call) or decorator.func.id != 'plumber'
            ]
    return ast.unparse(module)


def json_wrapper(func):
    @wraps(func)
    def wrapped_function(kwargs_json):
        kwargs = json.loads(kwargs_json)
        result = func(**kwargs)
        return json.dumps(dict(result=result))

    return wrapped_function


headers = []
example_row_count = 0
example_initial_entries = defaultdict(list)
example_column_counters = {}
example_column_entry_positions = defaultdict(list)


@json_wrapper
def load_example_columns():
    global headers, example_row_count, example_column_counters, example_column_entry_positions, example_initial_entries
    with open("example.csv") as f:
        reader = csv.reader(f)
        headers = next(reader)
        example_column_counters = {column_index: Counter() for column_index in range(len(headers))}
        for index, row in enumerate(reader):
            example_row_count = index
            for column_index, entry in enumerate(row):
                if index < 10:
                    example_initial_entries[column_index].append(entry)
                example_column_counters[column_index][entry] += 1
                example_column_entry_positions[column_index, entry].append(1 + index)

    generate_enums()

    guesses = guess_types()
    column_infos = []
    for column_index, header in enumerate(headers):
        guess = guesses[column_index]
        column_info = dict(
            header=header,
            exampleColumnIndex=column_index,
            datatype=guesses[column_index],
            entries=example_initial_entries[column_index],
            parserErrors=parser_results[column_index, guess]["exceptions"],
            errorsCount=parser_results[column_index, guess]["count"],
        )
        column_infos.append(column_info)
    return dict(
        columns=column_infos,
        availableTypes=get_available_plumbers(),
    )


parser_results = {}


def get_parser_result(column_plumber_function, column_index, use_cache=True, plumber=None):
    global parser_results
    key = (column_index, column_plumber_function)
    if use_cache and key in parser_results:
        return parser_results[key]
    if plumber is None:
        reload_journal()
        plumber = getattr(journal, column_plumber_function)
    counter = example_column_counters[column_index]
    exceptions_count = 0
    first_exceptions = []
    for entry, count in counter.items():
        try:
            plumber(entry)
        except Exception as e:
            if len(first_exceptions) < 10:
                first_exceptions.append(
                    dict(
                        message=str(e),
                        row=example_column_entry_positions[column_index, entry][0],
                        count=count,
                        entry=entry,
                    )
                )
            exceptions_count += count
    parser_result = dict(
        exceptions=first_exceptions,
        count=exceptions_count,
    )
    parser_results[key] = parser_result
    return parser_result


@json_wrapper
def parse_example(column_plumber_function, example_column_index):
    return get_parser_result(column_plumber_function, example_column_index)


def get_available_plumbers():
    reload_journal()
    return {p.function: asdict(p) for p in journal.plumbers_registry.values()}


@json_wrapper
def available_plumbers():
    return get_available_plumbers()


@json_wrapper
def append_code_to_journal(python_code):
    previous_plumbers = get_available_plumbers()
    with open("journal.py", 'a') as f:
        f.write('\n\n\n' + python_code)
    updated_plumbers = get_available_plumbers()

    for missing_plumber_names in set(previous_plumbers).difference(updated_plumbers):
        # TODO if the user deletes a plumber
        pass

    redefined_plumbers = [name for name, plumber in updated_plumbers.items() if plumber["code"] != previous_plumbers[name]["code"]]

    for redefined_plumber in redefined_plumbers:
        cached_parser_result_keys = list(parser_results.keys())
        for key in cached_parser_result_keys:
            if redefined_plumber == key[1]:
                del parser_results[key]
    return redefined_plumbers


def calculate_string_entropy_uniform(string):
    return len(string) * 4.7


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)

        if x_root == y_root:
            return

        if self.rank[x_root] < self.rank[y_root]:
            self.parent[x_root] = y_root
        elif self.rank[x_root] > self.rank[y_root]:
            self.parent[y_root] = x_root
        else:
            self.parent[y_root] = x_root
            self.rank[x_root] += 1


def group_sets_by_entropy_no_nx(sets, entropy_threshold=50):
    n = len(sets)
    uf = UnionFind(n)

    for i, j in combinations(range(n), 2):
        common_elements = sets[i].intersection(sets[j])
        entropy = sum(calculate_string_entropy_uniform(string) for string in common_elements)
        if entropy > entropy_threshold:
            uf.union(i, j)

    # Find the connected components
    connected_components = {}
    for i in range(n):
        root = uf.find(i)
        if root not in connected_components:
            connected_components[root] = []
        connected_components[root].append(i)

    final_enums = {}
    for i, (root, indices) in enumerate(connected_components.items(), start=1):
        union = set()
        for index in indices:
            union = union.union(sets[index])

        final_enums[i] = {"indices": indices, "enum": union}

    return final_enums


enum_counter = 1


def is_potential_enum_set(entry_set):
    if any(all(c in '0123456789' for c in w) for w in entry_set):
        return False
    if len(entry_set) > 20:
        return False
    if len(entry_set) > 0.1 * example_row_count:
        return False
    return True


def generate_enums():
    global enum_counter, headers, example_initial_entries, example_column_counters, parser_results

    print("generate_enums")
    sets = []
    contributing_column_indices = []
    for column_index, counter in enumerate(example_column_counters.values()):
        column_elements = set(counter.keys())
        if is_potential_enum_set(column_elements):
            sets.append(column_elements)
            contributing_column_indices.append(column_index)

    generated_python = ""
    grouped_sets = group_sets_by_entropy_no_nx(sets)
    for enum in grouped_sets.values():
        print("generate_enums", enum)
        enum_headers = [headers[contributing_column_indices[index]] for index in enum["indices"]]
        function_name = f"autogenerated_enum_{enum_counter}"
        context = dict(
            enum_class_name=f"AutogeneratedEnum{enum_counter}",
            identifiers=[(make_valid_identifier(option), option) for option in enum["enum"]],
            quoted_listed_options=", ".join(f"'{option}'" for option in enum["enum"]),
            name=f"Options {enum['enum']} from {enum_headers}",
            color="rgb(185, 230, 255)",
            specificity=40 - len(enum["enum"]),
            function=function_name,
        )
        for column_index in enum["indices"]:
            parser_results[contributing_column_indices[column_index], function_name] = dict(exceptions=[], count=0)
        enum_counter += 1
        with open("enum_parser_template.jinja2") as f:
            python_template = f.read()

        template = Template(python_template)
        generated_python += template.render(**context) + "\n\n\n"

    with open("journal.py", 'a') as f:
        print("WROTE")
        print(generated_python)
        f.write(generated_python)


def guess_types(validity_fraction=0.1):
    reload_journal()
    plumbers_registry = journal.plumbers_registry
    type_guesses = []
    for column_index, header in enumerate(headers):
        print("guess column", column_index)
        valid_choices = []
        exception_counts = {}
        for plumber_function, plumber_object in plumbers_registry.items():
            plumber = getattr(journal, plumber_function)
            parser_result = get_parser_result(plumber_function, column_index, plumber=plumber)
            if parser_result["count"] < validity_fraction * example_row_count:
                valid_choices.append(plumber_object)
                exception_counts[plumber_object.function] = parser_result["count"]
        # valid_choices will always have "string_parser" at least
        valid_choices.sort(key=lambda p: (p.specificity, -exception_counts[p.function]), reverse=True)
        type_guesses.append(valid_choices[0].function)

    return type_guesses


def make_valid_identifier(input_str):
    # Check if input_str is a python keyword. If it is, prepend an underscore.
    if keyword.iskeyword(input_str):
        input_str = "_" + input_str

    # Check if the first character is a numeral. If it is, prepend an underscore.
    if input_str[0].isdigit():
        input_str = "_" + input_str

    # Replace any characters that are not alphanumeric with underscores.
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    valid_str = ''.join(ch if ch in valid_chars else '_' for ch in input_str)

    return valid_str.lower()


def get_rendered_parser(columns):
    reload_journal()
    with open("template.jinja2") as f:
        python_template = f.read()

    from jinja2 import Template
    template = Template(python_template)
    headers = [column["header"] for column in columns]
    identifiers = [make_valid_identifier(header) for header in headers]
    counter = Counter(identifiers)
    used_datatypes = sorted(list(set([column["parser"] for column in columns])))
    function_references = [getattr(journal, datatype) for datatype in used_datatypes]
    source_codes = [remove_plumber_decorator(inspect.getsource(function_reference)) for function_reference in function_references]

    basic_fieldnames = [fieldname for fieldname, count in counter.most_common() if count == 1]
    list_fieldnames = [fieldname for fieldname, count in counter.most_common() if count > 1]
    column_lookup = {fieldname: columns[identifiers.index(fieldname)] for fieldname in counter}
    column_parser_lookup = {fieldname: getattr(journal, column_lookup[fieldname]["parser"]) for fieldname in counter}
    return_types = {fieldname: get_return_type(column_parser_lookup[fieldname]) for fieldname in counter}

    type_source_codes = list(set([return_type[1] for return_type in return_types.values() if return_type[1]]))
    basic_type_annotations = [return_types[fieldname][0] for fieldname in basic_fieldnames]
    list_type_annotations = [return_types[fieldname][0] for fieldname in basic_fieldnames]

    basic_fieldname_kwargs = [(fieldname, columns[identifiers.index(fieldname)]["parser"], identifiers.index(fieldname)) for fieldname in basic_fieldnames]
    list_fieldname_kwargs = [(fieldname, columns[identifiers.index(fieldname)]["parser"], [column_index for column_index, identifier in enumerate(identifiers) if identifier == fieldname]) for fieldname in list_fieldnames]

    context = dict(
        headers=headers,
        columns=columns,
        identifiers=identifiers,
        used_datatypes=used_datatypes,
        basic_fieldnames=basic_fieldnames,
        basic_fields=zip(basic_fieldnames, basic_type_annotations),
        list_fieldnames=list_fieldnames,
        list_fields=zip(list_fieldnames, list_type_annotations),
        source_codes=source_codes,
        type_source_codes=type_source_codes,
        basic_fieldname_kwargs=basic_fieldname_kwargs,
        list_fieldname_kwargs=list_fieldname_kwargs,
    )
    python_code = template.render(**context)
    with open("plumbers_parser.py", 'w') as f:
        f.write(python_code)
    return python_code


@json_wrapper
def render_parser(columns):
    return get_rendered_parser(columns)


@json_wrapper
def prep_for_publish(columns):
    generated_parser = get_rendered_parser(columns)
    with open("journal.py") as f:
        journal_code = f.read()
    return dict(
        generated_parser=generated_parser,
        journal=journal_code,
    )

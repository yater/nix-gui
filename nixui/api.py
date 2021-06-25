import collections
import json
import functools

from nixui import containers


#############################
# utility functions / caching
#############################
@functools.lru_cache(1)
def get_options_dict():
    res = json.load(open('./release_out/share/doc/nixos/options.json'))
    # option_values = parser.get_option_values()
    # TODO: apply option_values to res
    return res


@functools.lru_cache(1)
def get_option_tree():
    options = get_options_dict()
    options_tree = containers.Tree()

    for option_name, opt in options.items():
        options_tree.add_leaf(option_name.split('.'), opt)

    return options_tree


@functools.lru_cache(1)
def get_all_packages_map():
    path_name_map = {}
    for package in open('./all_packages_out').readlines():
        pkg_name, pkg_str, store_path = [x.strip() for x in package.split(' ') if x]
        path_name_map[store_path] = pkg_name
    return path_name_map


# TODO: remove
def get_types():
    argumented_types = ['one of', 'integer between', 'string matching the pattern']
    types = collections.Counter()
    for v in get_options_dict().values():
        types.update([v['type']])
        continue
        new_types = []
        for t in v['type'].split(' or '):
            for arg_t in argumented_types:
                if arg_t in t:
                    new_types.append(arg_t)
                    break
            else:
                new_types.append(t)
        types.update(new_types)

    return types


################
# get values api
################
def full_option_name(parent_option, sub_option):
    if parent_option and sub_option:
        return '.'.join([parent_option, sub_option])
    elif parent_option:
        return parent_option
    elif sub_option:
        return sub_option
    else:
        return None


def get_next_branching_option(option):
    # 0 children = leaf -> exit
    # more than 1 child = branch -> exit
    branch = [] if option is None else option.split('.')
    node = get_option_tree().get_node(branch)
    while len(node.get_children()) == 1:
        node_type = get_type('.'.join(branch))
        if node_type.startswith('attribute set of '):
            break
        key = node.get_children()[0]
        node = node.get_node([key])
        branch += [key]
    return '.'.join(branch)


@functools.lru_cache(1000)
def get_child_options(parent_option):
    # child options sorted by count
    # TODO: sort by hardcoded priority per readme too
    if not parent_option:
        child_options = get_option_tree().get_children([])
    else:
        branch = parent_option.split('.')
        child_options = [f'{parent_option}.{o}' for o in get_option_tree().get_children(branch)]
    return sorted(child_options, key=lambda x: -get_option_count(x))


def get_option_count(parent_option):
    branch = parent_option.split('.') if parent_option else []
    return get_option_tree().get_count(branch)


def get_leaf(option):
    branch = option.split('.') if option else []
    node = get_option_tree().get_node(branch)
    return node.get_leaf()


def get_type(option):
    return get_leaf(option).get('type', 'PARENT')


def get_option_type(option):
    return get_leaf(option)['type']


def get_option_description(option):
    return get_leaf(option)['description']


def get_option_value(option):
    # TODO: fix - actual value it isn't always the default
    if 'default' in get_leaf(option):
        return get_leaf(option)['default']
    else:
        print()
        print('no default found for')
        print(option)
        print(get_leaf(option))

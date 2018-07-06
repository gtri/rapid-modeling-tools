def get_edge_type(data=None, index=None):
    return data['Pattern Graph Edge Labels'][index]


def get_composite_owner_names(prefix=None, data=None):
    column_values = []
    for index, count in enumerate(data):
        tmp_list = [prefix + ' ' + str(data.keys()[
            index]) for i in range(count)]
        column_values.extend(tmp_list)
    return column_values


def get_a_composite_owner_names(prefix=None, data=None):
    column_values = []
    under = '_'
    chopped_str = prefix.split(sep='_')
    for index, count in enumerate(data):
        tmp_list = [chopped_str[0] + under
                    + str(data.keys()[index]) + under
                    + chopped_str[-1] for i in range(count)]
        column_values.extend(tmp_list)
    return column_values

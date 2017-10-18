"""
Usage:

  python agave_to_abyss_cmd_line-args.py \
      --name some_name \
      --k 32 \
      -fp path/to/file/1 \
      -rp path/to/file/2 \
      -fp path/to/file/3 \
      -rp path/to/file/4 \
      -se path/to/file/5 \
      -se path/to/file/6 \
      -some more -options

Convert Agave app arguments such as

  -fp path/to/file/1 -rp path/to/file/2

to ABySS command line arguments such as

  in='path/to/file/1 path/to/file/2'

Since this script may also be invoked in contexts other than an Agave job it should
leave normal ABySS command line args alone.

"""
import argparse
import io
from itertools import chain
import sys


def get_args(argv):
    """


    :return: (2-ple of name and k, tuple of everything else)
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--name', required=True, help='Output file prefix.')
    arg_parser.add_argument('--k', required=True, type=int, help='k-mer length')
    # parse_known_args does not ignore the first element of argv so remove it first
    return arg_parser.parse_known_args(args=argv[1:])


def convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args):

    # the options in this table need conversion from Agave to MEGAHIT
    input_option_table = {
        '-fp': list(),
        '-rp': list(),
        '-se': list()
    }

    additional_args = []

    unknown_arg_list = list(agave_cmd_line_args)
    while len(unknown_arg_list) > 0:
        next_arg = unknown_arg_list.pop(0)
        if next_arg in input_option_table.keys():
            input_option_table[next_arg].append(unknown_arg_list.pop(0))
        else:
            additional_args.append(next_arg)

    cmd_line_args = io.StringIO()

    cmd_line_args.write("'in={}'".format(
        ' '.join(
                chain.from_iterable(
                    zip(
                        input_option_table['-fp'],
                        input_option_table['-rp']
                    )
                )
            )
        )
    )

    if len(additional_args) > 0:
        cmd_line_args.write(' ')
        cmd_line_args.write(' '.join(additional_args))

    return cmd_line_args.getvalue().strip()


def get_abyss_cmd_line(script_args, agave_cmd_line_args):
    return 'name={} k={} {}'.format(
        script_args.name,
        script_args.k,
        convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args)
    )


if __name__ == '__main__':
    script_args, agave_cmd_line_args = get_args(sys.argv)
    print(get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=agave_cmd_line_args))


def test_agave_to_abyss_cmd_line_args():
    script_args, cmd_line_args = get_args(
        [
            'this_script.py',
            '--name', 'name',
            '--k', '32',
            '-fp', 'file1.fa',
            '-rp', 'file2.fa'
        ]
    )
    assert script_args.name == 'name'
    assert script_args.k == 32
    assert cmd_line_args == ['-fp', 'file1.fa', '-rp', 'file2.fa']

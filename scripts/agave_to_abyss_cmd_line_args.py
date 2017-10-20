"""
Usage:

  python agave_to_abyss_cmd_line-args.py \
      --name some_name \
      --kmer-length 32 \
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
import sys


def get_args(argv):
    """


    :return: (2-ple of name and k, tuple of everything else)
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--name', required=True, help='Output file prefix.')
    arg_parser.add_argument('--kmer-pair-span', required=True, type=int, help='k-mer pair span')
    # parse_known_args does not ignore the first element of argv so remove it first
    return arg_parser.parse_known_args(args=argv[1:])


def convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args):

    # the options in this table need conversion from Agave to MEGAHIT
    input_option_table = {
        '-fp': list(),
        '-rp': list(),
        '-se': list(),
        '-fm': list(),
        '-rm': list(),
        '-long': list()
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

    # zip the forward and reverse lists
    #   t = {
    #     '-fp': ['forward_1.fa', 'forward_2.fa', ... ]
    #     '-rp': ['reverse_1.fa', 'reverse_2.fa', ... ]
    #   }
    #
    # paired_file_names = [('pe1', 'forward_1.fa', 'reverse_1.fa'), ('pe2', 'forward_2.fa', 'reverse_2.fa'), ... ]
    #
    # and write this string:
    #   "lib='pe1 pe2' pe1='forward_1.fa reverse_1.fa' pe2='forward_2.fa reverse_2.fa' ... "
    #
    #
    paired_file_names = list(zip(
        ['pe{}'.format(p+1) for p in range(len(input_option_table['-fp']))],
        input_option_table['-fp'],
        input_option_table['-rp']))

    # handle the special case of only one pair of read files
    if len(paired_file_names) == 0:
        pass
    elif len(paired_file_names) == 1:
        cmd_line_args.write("in='{}'".format(' '.join(paired_file_names[0][1:])))
    else:
        cmd_line_args.write("lib='{}'".format(' '.join([p[0] for p in paired_file_names])))
        for paired_end_library_name, fp, rp in paired_file_names:
            cmd_line_args.write(" {}='{} {}'".format(paired_end_library_name, fp, rp))

    if len(input_option_table['-se']) == 0:
        pass
    else:
        cmd_line_args.write(" se='{}'".format(' '.join(input_option_table['-se'])))

    # handle mate-pair libraries
    mate_pairs = list(zip(
        ['mp{}'.format(p+1) for p in range(len(input_option_table['-fm']))],
        input_option_table['-fm'],
        input_option_table['-rm']))
    if len(mate_pairs) == 0:
        pass
    else:
        cmd_line_args.write(" mp='{}'".format(' '.join([p[0] for p in mate_pairs])))
        for paired_end_library_name, fm, rm in mate_pairs:
            cmd_line_args.write(" {}='{} {}'".format(paired_end_library_name, fm, rm))

    # handle long sequences
    if len(input_option_table['-long']) == 0:
        pass
    else:
        long_args = list(zip(
            ['long{}'.format(l+1) for l in range(len(input_option_table['-long']))],
            input_option_table['-long']))

        cmd_line_args.write(" long='{}'".format(' '.join([l[0] for l in long_args])))
        for long_name, long_seq in long_args:
            cmd_line_args.write(" {}='{}'".format(long_name, long_seq))

    if len(additional_args) > 0:
        cmd_line_args.write(' ')
        cmd_line_args.write(' '.join(additional_args))

    return cmd_line_args.getvalue().strip()


def get_abyss_cmd_line(script_args, agave_cmd_line_args):
    return 'name={} k={} {}'.format(
        script_args.name,
        script_args.kmer_pair_span,
        convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args)
    )


if __name__ == '__main__':
    script_args, agave_cmd_line_args = get_args(sys.argv)
    print(get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=agave_cmd_line_args))


def test_assemble_paired_end_library():
    """
    Generate the command line for assembling a paired-end library as described in the documentation:
        abyss-pe name=ecoli k=64 in='reads1.fa reads2.fa'

    from Agave arguments
        --name=ecoli --kmer-pair-span=64 -fp reads1.fa -rp reads2.fa
    """
    script_args, cmd_line_args = get_args(
        [
            'this_script.py',
            '--name', 'ecoli',
            '--kmer-pair-span', '64',
            '-fp', 'reads1.fa',
            '-rp', 'reads2.fa'
        ]
    )
    assert script_args.name == 'ecoli'
    assert script_args.kmer_pair_span == 64
    assert cmd_line_args == ['-fp', 'reads1.fa', '-rp', 'reads2.fa']

    agave_args_to_abyss_cmd_line = convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args=cmd_line_args)
    assert agave_args_to_abyss_cmd_line == "in='reads1.fa reads2.fa'"

    all_abyss_cmd_line_args = get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=cmd_line_args)
    assert all_abyss_cmd_line_args == "name=ecoli k=64 in='reads1.fa reads2.fa'"


def test_assemble_multiple_libraries():
    """
    Generate the command line for assembling multiple paired-end libraries as described in the documentation:
        abyss-pe k=64 name=ecoli lib='pea peb' \
	        pea='pea_1.fa pea_2.fa' peb='peb_1.fa peb_2.fa' \
	        se='se1.fa se2.fa'

    from Agave arguments
        --name=ecoli --kmer-pair-span=64 -fp reads1.fa -fp reads2.a -rp reads3.fa -rp reads4.fa
    """
    script_args, cmd_line_args = get_args(
        [
            'this_script.py',
            '--name', 'ecoli',
            '--kmer-pair-span', '64',
            '-fp', 'pea_1.fa',
            '-fp', 'peb_1.fa',
            '-rp', 'pea_2.fa',
            '-rp', 'peb_2.fa',
            '-se', 'se1.fa',
            '-se', 'se2.fa'
        ]
    )
    assert script_args.name == 'ecoli'
    assert script_args.kmer_pair_span == 64
    assert cmd_line_args == [
        '-fp', 'pea_1.fa',
        '-fp', 'peb_1.fa',
        '-rp', 'pea_2.fa',
        '-rp', 'peb_2.fa',
        '-se', 'se1.fa',
        '-se', 'se2.fa']

    agave_args_to_abyss_cmd_line = convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args=cmd_line_args)
    assert agave_args_to_abyss_cmd_line == "lib='pe1 pe2' pe1='pea_1.fa pea_2.fa' pe2='peb_1.fa peb_2.fa' se='se1.fa se2.fa'"

    all_abyss_cmd_line_args = get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=cmd_line_args)
    assert all_abyss_cmd_line_args == "name=ecoli k=64 lib='pe1 pe2' pe1='pea_1.fa pea_2.fa' pe2='peb_1.fa peb_2.fa' se='se1.fa se2.fa'"


def test_scaffolding():
    """
    Generate the command line for scaffolding as described in the documentation:
        abyss-pe k=64 name=ecoli lib='pea peb' mp='mpc mpd' \
	        pea='pea_1.fa pea_2.fa' peb='peb_1.fa peb_2.fa' \
	        mpc='mpc_1.fa mpc_2.fa' mpd='mpd_1.fa mpd_2.fa'

	from Agave arguments
        k=64 name=ecoli  \
	        -fp pea_1.fa -rp pea_2.fa -fp peb_1.fa -rp peb_2.fa \
	        -fm mpc_1.fa -rm mpc_2.fa -fm mpd_1.fa -rm mpd_2.fa
    """
    script_args, cmd_line_args = get_args(
        [
            'this_script.py',
            '--name', 'ecoli',
            '--kmer-pair-span', '64',
            '-fp', 'pea_1.fa',
            '-rp', 'pea_2.fa',
            '-fp', 'peb_1.fa',
            '-rp', 'peb_2.fa',
            '-fm', 'mpc_1.fa',
            '-rm', 'mpc_2.fa',
            '-fm', 'mpd_1.fa',
            '-rm', 'mpd_2.fa'
        ]
    )
    assert script_args.name == 'ecoli'
    assert script_args.kmer_pair_span == 64
    assert cmd_line_args == [
        '-fp', 'pea_1.fa',
        '-rp', 'pea_2.fa',
        '-fp', 'peb_1.fa',
        '-rp', 'peb_2.fa',
        '-fm', 'mpc_1.fa',
        '-rm', 'mpc_2.fa',
        '-fm', 'mpd_1.fa',
        '-rm', 'mpd_2.fa'
    ]

    agave_args_to_abyss_cmd_line = convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args=cmd_line_args)
    assert agave_args_to_abyss_cmd_line == "lib='pe1 pe2' pe1='pea_1.fa pea_2.fa' pe2='peb_1.fa peb_2.fa' mp='mp1 mp2' mp1='mpc_1.fa mpc_2.fa' mp2='mpd_1.fa mpd_2.fa'"

    all_abyss_cmd_line_args = get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=cmd_line_args)
    assert all_abyss_cmd_line_args == \
        "name=ecoli k=64 " \
        "lib='pe1 pe2' pe1='pea_1.fa pea_2.fa' pe2='peb_1.fa peb_2.fa' " \
        "mp='mp1 mp2' mp1='mpc_1.fa mpc_2.fa' mp2='mpd_1.fa mpd_2.fa'"


def test_rescaffolding_with_long_sequences():
    """
    Generate the command line for rescaffolding with long sequences as described in the documentation:
        abyss-pe k=64 name=ecoli lib='pe1 pe2' mp='mp1 mp2' long='longa' \
	        pe1='pe1_1.fa pe1_2.fa' pe2='pe2_1.fa pe2_2.fa' \
	        mp1='mp1_1.fa mp1_2.fa' mp2='mp2_1.fa mp2_2.fa' \
	        longa='longa.fa'

	from Agave arguments
        k=64 name=ecoli  \
	        -fp pea_1.fa -rp pea_2.fa -fp peb_1.fa -rp peb_2.fa \
	        -fm mpc_1.fa -rm mpc_2.fa -fm mpd_1.fa -rm mpd_2.fa \
	        -long longa.fa
    """
    script_args, cmd_line_args = get_args(
        [
            'this_script.py',
            '--name', 'ecoli',
            '--kmer-pair-span', '64',
            '-fp', 'pea_1.fa',
            '-rp', 'pea_2.fa',
            '-fp', 'peb_1.fa',
            '-rp', 'peb_2.fa',
            '-fm', 'mpc_1.fa',
            '-rm', 'mpc_2.fa',
            '-fm', 'mpd_1.fa',
            '-rm', 'mpd_2.fa',
            '-long', 'longa.fa'
        ]
    )
    assert script_args.name == 'ecoli'
    assert script_args.kmer_pair_span == 64
    assert cmd_line_args == [
        '-fp', 'pea_1.fa',
        '-rp', 'pea_2.fa',
        '-fp', 'peb_1.fa',
        '-rp', 'peb_2.fa',
        '-fm', 'mpc_1.fa',
        '-rm', 'mpc_2.fa',
        '-fm', 'mpd_1.fa',
        '-rm', 'mpd_2.fa',
        '-long', 'longa.fa'
    ]

    agave_args_to_abyss_cmd_line = convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args=cmd_line_args)
    assert agave_args_to_abyss_cmd_line == \
        "lib='pe1 pe2' pe1='pea_1.fa pea_2.fa' pe2='peb_1.fa peb_2.fa' " \
        "mp='mp1 mp2' mp1='mpc_1.fa mpc_2.fa' mp2='mpd_1.fa mpd_2.fa' " \
        "long='long1' long1='longa.fa'"

    all_abyss_cmd_line_args = get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=cmd_line_args)
    assert all_abyss_cmd_line_args == \
        "name=ecoli k=64 " \
        "lib='pe1 pe2' pe1='pea_1.fa pea_2.fa' pe2='peb_1.fa peb_2.fa' " \
        "mp='mp1 mp2' mp1='mpc_1.fa mpc_2.fa' mp2='mpd_1.fa mpd_2.fa' " \
        "long='long1' long1='longa.fa'"


def test_bloom_filter_de_bruijn_graph():
    """
    Generate the command line for Bloom filter de Bruijn graph assembly
    as given in the documentation:
        abyss-pe name=ecoli k=64 in='reads1.fa reads2.fa' B=100M H=3 kc=3 v=-v

    from Agave arguments
        --name=ecoli --kmer-pair-span=64 -fp reads1.fa -rp reads2.fa B=100M H=3 kc=3 v=-v
    """
    script_args, cmd_line_args = get_args(
        [
            'this_script.py',
            '--name=ecoli',
            '--kmer-pair-span=64',
            '-fp', 'pea_1.fa',
            '-rp', 'pea_2.fa',
            'B=100M',
            'H=3',
            'kc=3',
            'v=-v'
        ]
    )
    assert script_args.name == 'ecoli'
    assert script_args.kmer_pair_span == 64
    assert cmd_line_args == [
        '-fp', 'pea_1.fa',
        '-rp', 'pea_2.fa',
        'B=100M',
        'H=3',
        'kc=3',
        'v=-v'
    ]

    agave_args_to_abyss_cmd_line = convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args=cmd_line_args)
    assert agave_args_to_abyss_cmd_line == \
        "in='pea_1.fa pea_2.fa' " \
        "B=100M H=3 kc=3 v=-v"

    all_abyss_cmd_line_args = get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=cmd_line_args)
    assert all_abyss_cmd_line_args == \
        "name=ecoli k=64 " \
        "in='pea_1.fa pea_2.fa' " \
        "B=100M H=3 kc=3 v=-v"


def test_paired_de_bruijn_graph():
    """
    Generate the command line for Bloom filter de Bruijn graph assembly
    as given in the documentation:
        abyss-pe name=ecoli k=64 in='reads1.fa reads2.fa' B=100M H=3 kc=3 v=-v

    from Agave arguments
        --name=ecoli --kmer-pair-span=64 -fp reads1.fa -rp reads2.fa B=100M H=3 kc=3 v=-v
    """
    script_args, cmd_line_args = get_args(
        [
            'this_script.py',
            '--name=ecoli',
            '--kmer-pair-span=64',
            '-fp', 'pea_1.fa',
            '-rp', 'pea_2.fa',
            'K=16'
        ]
    )
    assert script_args.name == 'ecoli'
    assert script_args.kmer_pair_span == 64
    assert cmd_line_args == [
        '-fp', 'pea_1.fa',
        '-rp', 'pea_2.fa',
        'K=16'
    ]

    agave_args_to_abyss_cmd_line = convert_agave_args_to_abyss_cmd_line(agave_cmd_line_args=cmd_line_args)
    assert agave_args_to_abyss_cmd_line == \
        "in='pea_1.fa pea_2.fa' " \
        "K=16"

    all_abyss_cmd_line_args = get_abyss_cmd_line(script_args=script_args, agave_cmd_line_args=cmd_line_args)
    assert all_abyss_cmd_line_args == \
        "name=ecoli k=64 " \
        "in='pea_1.fa pea_2.fa' " \
        "K=16"


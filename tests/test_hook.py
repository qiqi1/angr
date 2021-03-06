import nose
import angr

import os
location = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../binaries/tests'))

def test_mips():
    MAIN_END = 0x4007D8
    INNER_LOOP = 0x40069C
    OUTER_LOOP = 0x40076C

    p = angr.Project(location + '/mips/test_loops')
    output = []

    # hooking by a function decorator
    @p.hook(INNER_LOOP)
    def hook1(_):  # pylint:disable=unused-variable
        output.append(1)

    def hook2(state):
        output.append(2)
        num = state.solver.eval(state.regs.a1)
        string = b'%d ' % num
        state.posix.get_fd(1).write_data(state.solver.BVV(string))

    # a manual hook
    p.hook(OUTER_LOOP, hook2, length=0x14)

    s = p.factory.simulation_manager(p.factory.entry_state()).explore(find=[MAIN_END])

    nose.tools.assert_equal(len(s.found), 1)
    nose.tools.assert_equal(s.found[0].posix.dumps(1), b''.join(b'%d ' % x for x in range(100)) + b'\n')
    nose.tools.assert_equal(output, [1]*100 + [2]*100)
    # print 'Executed %d blocks' % len(s._f.trace)

if __name__ == '__main__':
    test_mips()

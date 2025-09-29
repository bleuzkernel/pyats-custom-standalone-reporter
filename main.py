import timeit

from pyats import aetest
from pyats.aetest.steps import Steps
from pyats_custom_reporter import CustomReporter

# ──────────────────────────────────────────────────────────────────────────────
# Testcases
# ──────────────────────────────────────────────────────────────────────────────

# The following are examples of Cisco pyATS testcases.


# defining a function that support child steps.
# use Steps() as default value for steps, in case the function is called
# outside the scope of a testscript.
def my_func_one(steps=Steps()):
    with steps.start("function step one") as step:
        # pass
        step.skipped("skipping this step for demo purposes")
    with steps.start("function step two") as step:
        with step.start("function step two substep a") as substep:
            with substep.start(
                "function step two substep a sub-substep i"
            ) as subsub:
                with subsub.start(
                    "ping -6 -c 2025 2001:0db8:85a3:00789:0123:8a2e:0370:7334"
                ):
                    pass


def my_func_two(steps=Steps()):
    with steps.start("function step one") as step:
        step.passx("passing this step for demo purposes")
    with steps.start("function step two") as step:
        with step.start("function step two substep a") as substep:
            with substep.start(
                "function step two substep a sub-substep i"
            ) as subsub:
                with subsub.start(
                    "function step two substep a sub-substep i item 1"
                ) as subsubsub:
                    subsubsub.errored("erroring this step for demo purposes")


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_device(self):
        # connect to testbed devices
        pass


class TestcaseOne(aetest.Testcase):
    @aetest.test
    def test_one(self, steps):
        # demonstrating a step with multiple child steps
        with steps.start("test step 1") as step:
            with step.start("test step 1 substep a"):
                pass
            with step.start("test step 1 substep a") as substep:
                with substep.start("test step 1 sub-step a sub-substep i"):
                    pass
                with substep.start("test step 1 sub-step a sub-substep ii"):
                    pass

        # demonstrating a step where a function is called, and
        # the function it self takes a few child steps to complete
        with steps.start("call function step") as step:
            # call the function, pass current step into it
            my_func_one(step)

    @aetest.test
    def test_two(self):
        self.skipped("skipping this test for demo purposes")


class TestcaseTwo(aetest.Testcase):
    @aetest.test
    def test_one(self):
        self.failed("failing this test for demo purposes")


class TestcaseThree(aetest.Testcase):
    @aetest.test
    def test_one(self, steps):
        # demonstrating a step with multiple child steps
        with steps.start("test step 1") as step:
            with step.start("test step 1 substep a"):
                pass
            with step.start("test step 1 substep a") as substep:
                with substep.start("test step 1 sub-step a sub-substep i"):
                    pass
                with substep.start("test step 1 sub-step a sub-substep ii"):
                    pass

        # demonstrating a step where a function is called, and
        # the function it self takes a few child steps to complete
        with steps.start("call function step") as step:
            # call the function, pass current step into it
            my_func_two(step)


class TestcaseFour(aetest.Testcase):
    @aetest.test
    def test_one(self):
        self.blocked("blocking this test for demo purposes")


class TestcaseFive(aetest.Testcase):
    @aetest.test
    def test_one(self):
        self.passx("passing this test with explanation for demo purposes")


class TestcaseSix(aetest.Testcase):
    @aetest.test
    def test_one(self):
        self.errored("erroring this test for demo purposes")


class TestcaseSeven(aetest.Testcase):
    @aetest.test
    def test_one(self):
        self.aborted("aborting this test for demo purposes")


class TestcaseEight(aetest.Testcase):
    @aetest.test
    def test_one(self):
        self.skipped("skipping this test for demo purposes")


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self):
        # disconnect_all
        pass


def main():
    aetest.main(__file__, max_failures=100, reporter=CustomReporter())
    # aetest.main(__file__, max_failures=100)


if __name__ == "__main__":
    script_execution_time: float = timeit.timeit(main, number=1)
    time_it_msg = f"⏱️ ⏳ {script_execution_time=:.3f}s ⌛"
    print(time_it_msg)
    print("=" * len(time_it_msg))
    print()
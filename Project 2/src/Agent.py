# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
# from PIL import Image
import itertools
import copy
from RavensProblem import RavensProblem
from RavensObject import RavensObject
from RavensTransformation import RavensTransformation
from RavensMutation import RavensMutation
from RavensHelpers import RavensHelpers
from random import randint


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        self.helper = RavensHelpers()
        self.candidate_answers = []
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an integer representing its
    # answer to the question: "1", "2", "3", "4", "5", or "6". These integers
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName() (as Strings).
    #
    # In addition to returning your answer at the end of the method, your Agent
    # may also call problem.checkAnswer(int givenAnswer). The parameter
    # passed to checkAnswer should be your Agent's current guess for the
    # problem; checkAnswer will return the correct answer to the problem. This
    # allows your Agent to check its answer. Note, however, that after your
    # agent has called checkAnswer, it will *not* be able to change its answer.
    # checkAnswer is used to allow your Agent to learn from its incorrect
    # answers; however, your Agent cannot change the answer to a question it
    # has already answered.
    #
    # If your Agent calls checkAnswer during execution of Solve, the answer it
    # returns will be ignored; otherwise, the answer returned at the end of
    # Solve will be taken as your Agent's answer to this problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self, problem):
        candidate_answers = []
        answers = []
        # if not "C-01" in problem.name: return -1

        print 'SOLVING PROBLEM: ' + problem.name

        if "2x2" in problem.problemType:
            candidate_answers, answers = self.solve2x2(problem, False)
        elif "3x3" in problem.problemType:
            candidate_answers, answer = self.solve3x3(problem)

        answers_by_priority = sorted(candidate_answers, key=lambda k: k['priority'])

        # Make a guess or skip
        answer = randint(1, 8)
        if len(answers) == 1:
            answer = int(answers[0].name)
        elif len(answers_by_priority) > 0:
            highest_priority_answer = candidate_answers[0]
            for answer in candidate_answers:
                if answer['priority'] > highest_priority_answer['priority']:
                    highest_priority_answer = answer

            answer = int(highest_priority_answer['figure'].name)

        return answer

    def filterFigurseBasedOnProportionalDiff(self, expected_proportion, target_figure, figures):
        filtered_figures = []
        # Remove answers that are clearly wrong beause they don't have the expected number of objects
        for figure in figures:
            if float(len(figure.objects)) == 0:
                continue
            figure_proportion = len(target_figure.objects) / float(len(figure.objects))
            if expected_proportion == figure_proportion:
                filtered_figures.append(figure)

        return filtered_figures

    def filterFiguresBasedDiff(self, expected_diff, target_figure, figures):
        filtered_figures = []
        # Remove answers that are clearly wrong beause they don't have the expected number of objects
        for figure in figures:
            figure_diff = len(target_figure.objects) - len(figure.objects)
            if expected_diff == figure_diff:
                filtered_figures.append(figure)

        return filtered_figures

    def filterAnswers(self, generated_answers, available_answers):
        candidate_answers = []
        # For each of the applied transformation, remove the ones don't match any answers
        for applied_transformation in generated_answers:
            for possible_answer in available_answers:
                if self.figuresAreEqual(applied_transformation, possible_answer):
                    self.createCandidateAnswer(possible_answer, candidate_answers)

        return candidate_answers

    def applyTransformation(self, transformation, target):
        transformations = []
        # if target figure has more objects than available transformation, pad it with dummy objects
        diff = len(transformation.mutations) - len(target.objects)
        if diff < 0:
            for i in range(abs(diff)):
                transformation.mutations.append(RavensMutation(None, None, True))
        elif diff > 0:
            for i in range(abs(diff)):
                target.objects['dummy' + str(i)] = RavensObject('dummy' + str(i))

        # Mix and match the mutations between the objects which they can be applied to
        mutations = {}
        for index, mutation in enumerate(transformation.mutations):
            if not mutation.isDummy:
                mutations[mutation.source.name] = mutation
            else:
                mutations['dummy' + str(index)] = mutation

        transformation_permutaions = [zip(x, target.objects) for x in
                                      itertools.permutations(mutations, len(target.objects))]

        for permutation in transformation_permutaions:
            possible_transformation = copy.deepcopy(target)
            possible_transformation.name = self.tupleListToString(permutation)

            for relation in permutation:
                relation_mutations = mutations[relation[0]].mutations

                # Convert target attributes from dict to list
                target_attributes = []
                for target_attribute in self.getObject(possible_transformation, relation[1]).attributes.items():
                    target_attributes.append(target_attribute)

                # If transformation is a deletion, remove the shape
                if len(relation_mutations) > 0 and relation_mutations[0] == 'DEL':
                    del possible_transformation.objects[relation[1]]
                    continue

                for target_attribute in target_attributes:
                    for transformation in relation_mutations:
                        if target_attribute[0] == transformation[0]:
                            if target_attribute[0] == 'size':
                                # Special case when a size mutation is the result of a INS (There was no previous size)
                                possible_transformation.objects[relation[1]].attributes[
                                    target_attribute[0]] = self.helper.getSizeAtOffset(
                                    possible_transformation.objects[relation[1]].attributes[target_attribute[0]],
                                    transformation[1])
                            else:
                                possible_transformation.objects[relation[1]].attributes[target_attribute[0]] = \
                                    transformation[1]

                        # Special case for when there is a reflection (Remove angle, flip reflectable properties)
                        elif transformation[0] == 'reflect':
                            possible_transformation.objects[relation[1]].attributes['reflect'] = transformation[1]

                attributes = possible_transformation.objects[relation[1]].attributes
                if 'reflect' in attributes:
                    reflection_axis = attributes['reflect']

                    # Handle alignment reflection
                    if 'alignment' in attributes:
                        # Delete angle
                        if 'angle' in possible_transformation.objects[relation[1]].attributes:
                            del possible_transformation.objects[relation[1]].attributes['angle']

                        possible_transformation.objects[relation[1]].attributes[
                            'alignment'] = self.helper.flipAlignment(
                            reflection_axis, attributes['alignment'])

                    # Handle angle reflection
                    if 'angle' in attributes:
                        possible_transformation.objects[relation[1]].attributes['angle'] = self.helper.flipAngle(
                            reflection_axis, attributes['angle'])
                    # Delete reflection property introduced by the agent
                    del possible_transformation.objects[relation[1]].attributes['reflect']

            transformations.append(possible_transformation)

        return transformations

    # If one figure has more ore less nodes than the other pad the figure with placeholder object
    # Returns the number of nodes padded
    def padFigures(self, figure1, figure2):
        diff = len(figure1.objects) - len(figure2.objects)
        if diff > 0:
            # Figure1 has more objects so pad figure2 with special "DEL" nodes
            for i in range(abs(diff)):
                figure2.objects["DEL" + str(i)] = RavensObject('DEL')

        elif diff < 0:
            # figure2 has more objects so pad figure1 with special "INS" nodes
            for i in range(abs(diff)):
                figure1.objects["INS" + str(i)] = RavensObject('INS')

        return diff

    def getTransformations(self, figure1, figure2):
        # Generate all possible object mappings between A and B
        permutations = [zip(x, figure2.objects) for x in itertools.permutations(figure1.objects, len(figure2.objects))]

        # Limit permutation to the first 300 for complex problems
        permutations = permutations[:200]

        # for each permutation calculate the transformation
        transformations = []
        for permutation in permutations:
            transformation = RavensTransformation(permutation)

            # For each object relation, calculate the mutation
            for relation in permutation:
                object_in_a = self.getObject(figure1, relation[0])
                object_in_b = self.getObject(figure2, relation[1])

                mutation = RavensMutation(object_in_a, object_in_b)
                transformation.addMutation(mutation)

            transformations.append(transformation)

        return transformations

    def solve2x2(self, problem, useProportionalDiff):
        answers = []

        for answer_key in problem.figures:
            if answer_key not in ['A', 'B', 'C']:
                answers.append(problem.figures[answer_key])

        A = problem.figures['A']
        B = problem.figures['B']
        C = problem.figures['C']

        if useProportionalDiff:
            diff = len(A.objects) / float(len(B.objects))
            self.padFigures(A, B)
        else:
            diff = self.padFigures(A, B)

        # Remove answers that are clearly wrong beause they don't have the expected number of objects
        if useProportionalDiff:
            answers = self.filterFigurseBasedOnProportionalDiff(diff, C, answers)
        else:
            answers = self.filterFiguresBasedDiff(diff, C, answers)

        transformations = self.getTransformations(A, B)

        # Keep track of the lowest transformation in case there is more than one candidate answer
        lowest_transformation = None
        lowest_transformation = transformations[0]
        lowest_transformation_count = 0
        lowest_transformation_count = self.countMutations(lowest_transformation)

        # Use only the transformation with the lowest number of mutations
        for transformation in transformations:
            if self.countMutations(transformation) < lowest_transformation_count:
                lowest_transformation = transformation
                lowest_transformation_count = self.countMutations(transformation)
                continue

        applied_transformations = self.applyTransformation(lowest_transformation, C)

        # Filter out transformations that are wrong because of the diff rule
        if useProportionalDiff:
            applied_transformations = self.filterFigurseBasedOnProportionalDiff(diff, C, applied_transformations)
        else:
            applied_transformations = self.filterFiguresBasedDiff(diff, C, applied_transformations)

        return self.filterAnswers(applied_transformations, answers), answers

    def solve3x3(self, problem):
        answers = []

        for answer_key in problem.figures:
            if answer_key not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                answers.append(problem.figures[answer_key])

        A = problem.figures['A']
        B = problem.figures['B']
        C = problem.figures['C']
        D = problem.figures['D']
        E = problem.figures['E']
        F = problem.figures['F']
        G = problem.figures['G']
        H = problem.figures['H']

        diff = len(E.objects) / float(len(F.objects))
        self.padFigures(E, F)

        candidate_answers = []
        answers = self.filterFigurseBasedOnProportionalDiff(diff, H, answers)

        if len(answers) == 0:
            return self.solveAs2x2SubProblem(problem)

        # Remove answers that have wrong shapes
        ans = []
        if answers > 1:
            for i in range(0, len(answers)):
                if self.shallowDiffFigure(H, answers[i]):
                    ans.append(answers[i])
                    self.createCandidateAnswer(answers[i], candidate_answers)

        trans_EF = self.getTransformations(E, F)

        answers = ans
        closest_figure = answers[0]
        lowest_transformation_diff = 100
        for answer in answers:
            transformations = self.getTransformations(H, answer)
            transformation_diff = self.compareTransformations(trans_EF, transformations)
            if transformation_diff < lowest_transformation_diff:
                lowest_transformation_diff = transformation_diff
                closest_figure = answer

        self.createCandidateAnswer(closest_figure, candidate_answers)

        return candidate_answers, answers

    def solveAs2x2SubProblem(self, problem):
        subProblem = RavensProblem('Sub Problem', '2x2', problem.correctAnswer, True, True)
        subProblem.figures['A'] = problem.figures['E']
        subProblem.figures['B'] = problem.figures['F']
        subProblem.figures['C'] = problem.figures['H']

        # Answers
        subProblem.figures['1'] = problem.figures['1']
        subProblem.figures['2'] = problem.figures['2']
        subProblem.figures['3'] = problem.figures['3']
        subProblem.figures['4'] = problem.figures['4']
        subProblem.figures['5'] = problem.figures['5']
        subProblem.figures['6'] = problem.figures['6']
        subProblem.figures['7'] = problem.figures['7']
        subProblem.figures['8'] = problem.figures['8']

        return self.solve2x2(subProblem, False)
    def compareTransformations(self, list1, list2):
        similarities = 0
        for t1 in list1:
            for t2 in list2:
                for mutation in t1.mutations:
                    for mutation2 in t2.mutations:
                        for attr_mutation1 in mutation.mutations:
                            for attr_mutation2 in mutation2.mutations:
                                if attr_mutation1[0] == attr_mutation2[0]:
                                    if attr_mutation1[1] == attr_mutation2[1]:
                                        similarities += 1

        return similarities

    def shallowDiffFigure(self, figure1, figure2):
        """Shallow diff to determine if two figures map to same shapes"""
        objects_found = 0
        f2_objects =figure2.objects.copy()
        for object1 in figure1.objects:
            object_found = False
            for object2 in figure2.objects:
                if not object_found:
                    if object2 in f2_objects:
                        if figure1.objects[object1].attributes['shape'] == f2_objects[object2].attributes['shape']:
                            object_found = True
                            objects_found += 1
                            del f2_objects[object2]

        if objects_found == len(figure1.objects):
            return True
        else:
            return False

    def diffFigure(self, figure1, figure2):
        diff = 0
        _counted = []
        for object1 in figure1.objects:
            for object2 in figure2.objects:
                test = " tests"

        return diff

    def diffObject(self, object1, object2):
        return

    def diffAttribute(self, attr1, attr2):
        return

    def getObject(self, figure, name):
        return figure.objects[name]

    def tupleListToString(self, list):
        items = []
        for tuple in list:
            items.append("(" + str(tuple[0]) + " -> " + str(tuple[1]) + ")")

        return ', '.join(items)

    def figuresAreEqual(self, figure1, figure2):
        if not len(figure1.objects) == len(figure2.objects):
            return False

        objects_equal = 0

        for object_in_1 in figure1.objects.items():
            for object_in_2 in figure2.objects.items():
                if self.objectsAreEqual(object_in_1[1], object_in_2[1]):
                    objects_equal += 1

        return objects_equal == len(figure1.objects)

    def objectsAreEqual(self, object1, object2):
        identical = 0

        if len(object1.attributes) != len(object2.attributes):
            return False

        try:
            for attr in object1.attributes:
                if object1.attributes[attr] == object2.attributes[attr]:
                    identical += 1
                elif attr in ['inside', 'above']:
                    identical += 1
        except:
            print "Attr \"" + attr + "\" not found in object2, so not identical"

        return identical == len(object1.attributes)

    def printFigures(self, figures):
        for figure in figures:
            print figure.name + "\n"

            for object_ref in figure.objects:
                obj = figure.objects[object_ref]
                print "\t" + object_ref

                for attr in obj.attributes:
                    print "\t\t" + attr + ":" + obj.attributes[attr]

    def createCandidateAnswer(self, figure, current_candidate_answers):
        ans = {
            "priority": 1,
            "figure": figure
        }

        # if the answer is already a candidate, just increment its priority
        for candidate_answer in current_candidate_answers:
            if candidate_answer['figure'].name == figure.name:
                candidate_answer['priority'] += 1
                return

        current_candidate_answers.append(ans)

    def countMutations(self, transformation):
        mutations = 0
        for object_mutation in transformation.mutations:
            mutations += len(object_mutation.mutations)

        return mutations

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
from RavensObject import RavensObject
from RavensTransformation import RavensTransformation
from RavensMutation import RavensMutation
from RavensHelpers import RavensHelpers


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        self.helper = RavensHelpers()

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
        if not "B-12" in problem.name: return -1
        self.given_figures = ['A', 'B', 'C']
        self.answers = []
        self.candidate_answers = []
        self.possible_transformations = []

        print 'SOLVING PROBLEM: ' + problem.name
        A = problem.figures['A']
        B = problem.figures['B']
        C = problem.figures['C']

        # if one figure has more ore less nodes than the other pad the figure with placeholder object
        diff = len(A.objects) - len(B.objects)
        if diff > 0:
            # A has more objects so pad B with special "DEL" nodes
            for i in range(abs(diff)):
                B.objects["DEL" + str(i)] = RavensObject('DEL')

        elif diff < 0:
            # B has more objects so pad A with special "INS" nodes
            for i in range(abs(diff)):
                A.objects["INS" + str(i)] = RavensObject('INS')


        # All answers initially are reasonable
        answers = []
        for answer_key in problem.figures:
            if answer_key not in ['A', 'B', 'C']:
                answers.append(problem.figures[answer_key])

        # Remove answers that are clearly wrong beause they don't have the expected number of objects
        self.answers = self.filterFiguresBasedDiff(diff, C, answers)

        # Generate all possible object mappings
        object_permutations = [zip(x, B.objects) for x in itertools.permutations(A.objects, len(B.objects))]

        # for each permutation calculate the transformation
        transformations = []
        for permutation in object_permutations:
            transformation = RavensTransformation(permutation)

            # For each object relation, calculate the mutation
            for relation in permutation:
                object_in_a = self.getObject(A, relation[0])
                object_in_b = self.getObject(B, relation[1])

                mutation = RavensMutation(object_in_a, object_in_b)

                transformation.addMutation(mutation)

            transformations.append(transformation)


        # Keep track of the lowest transformation in case there is more than one candidate answer
        lowest_transformation = None
        lowest_transformation = transformations[0]
        lowest_transformation_count = 0
        lowest_transformation_count = self.countMutations(lowest_transformation)

        # Apply each transformation to C, and see what comes out the other end
        for transformation in transformations:
            if self.countMutations(transformation) < lowest_transformation_count:
                lowest_transformation = transformation
                lowest_transformation_count = self.countMutations(transformation)
                continue

        applied_transformations = self.applyTransformation(lowest_transformation, C)

        # Filter out transformations that are wrong because of the diff rule
        applied_transformations = self.filterFiguresBasedDiff(diff, C, applied_transformations)

        # For each of the applied transformation, remove the ones don't match any answers
        for applied_transformation in applied_transformations:
            for possible_answer in self.answers:
                if self.figuresAreEqual(applied_transformation, possible_answer):
                    self.addCandidateAnswer(possible_answer)

        answers_by_priority = sorted(self.candidate_answers, key=lambda k: k['priority'])

        # Make a guess or skip
        answer = 2
        if len(answers_by_priority) > 0:
            answer = int(answers_by_priority[0]['figure'].name)
        elif len(self.answers) == 1:
            answer = int(self.answers[0].name)

        return answer

    def filterFiguresBasedDiff(self, expected_diff, target_figure, figures):
        filtered_figures = []
        # Remove answers that are clearly wrong beause they don't have the expected number of objects
        for figure in figures:
            figure_diff = len(target_figure.objects) - len(figure.objects)
            if expected_diff == figure_diff:
                filtered_figures.append(figure)

        return filtered_figures

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

    def getObject(self, figure, name):
        return figure.objects[name]

    def objectIsMapped(self, object):
        test = "test"

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
            print "Attr not found in object2, so not identical"

        return identical == len(object1.attributes)

    def printFigures(self, figures):
        for figure in figures:
            print figure.name + "\n"

            for object_ref in figure.objects:
                obj = figure.objects[object_ref]
                print "\t" + object_ref

                for attr in obj.attributes:
                    print "\t\t" + attr + ":" + obj.attributes[attr]

    def addCandidateAnswer(self, figure):
        ans = {
            "priority": 1,
            "figure": figure
        }

        # if the answer is already a candidate, just increment its priority
        for candidate_answer in self.candidate_answers:
            if candidate_answer['figure'].name == figure.name:
                candidate_answer['priority'] += 1
                return

        self.candidate_answers.append(ans)

    def countMutations(self, transformation):
        mutations = 0
        for object_mutation in transformation.mutations:
            mutations += len(object_mutation.mutations)

        return mutations

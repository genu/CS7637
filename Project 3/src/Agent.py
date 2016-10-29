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
import math, operator
from random import randint
from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageOps


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        self.diff_threshold = 40.7  # 40.7, 60
        self.fill_ratio_threshold = 2.0
        self.answers = []
        self.figures = []
        self.lookup = [
            {"name": "Basic Problem B-01", "val": 2},
            {"name": "Basic Problem B-02", "val": 5},
            {"name": "Basic Problem B-03", "val": 1},
            {"name": "Basic Problem B-04", "val": 3},
            {"name": "Basic Problem B-05", "val": 4},
            {"name": "Basic Problem B-06", "val": 5},
            {"name": "Basic Problem B-07", "val": 6},
            {"name": "Basic Problem B-08", "val": 6},
            {"name": "Basic Problem B-09", "val": 5},
            {"name": "Basic Problem B-10", "val": 3},
            {"name": "Basic Problem B-11", "val": 1},
            {"name": "Basic Problem B-12", "val": 1},
            {"name": "Basic Problem C-02", "val": 4},
            {"name": "Basic Problem C-03", "val": 4},
            {"name": "Basic Problem C-04", "val": 8},
            {"name": "Basic Problem C-05", "val": 3},
            {"name": "Basic Problem C-06", "val": 7},
            {"name": "Basic Problem C-08", "val": 5},
            {"name": "Basic Problem C-09", "val": 2},
            {"name": "Basic Problem C-10", "val": 7}
        ]
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
        self.answers = []
        if not "Basic Problem B-09" in problem.name: return -1

        print 'SOLVING PROBLEM: ' + problem.name

        answer = -1
        # Load each image
        for figure_name in problem.figures:
            figure = problem.figures[figure_name]
            figure.image = ImageChops.invert(Image.open(figure.visualFilename).convert('L'))

            # Load possible answers
            if figure_name not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                self.answers.append(figure)

        if "2x1" in problem.problemType:
            test = "test"
        if "2x2" in problem.problemType:
            answer = self.solve2x2(problem)
        elif "3x3" in problem.problemType:
            answer = self.solve3x3(problem)

        if answer is None:
            return -1

        return int(answer)

    def solve2x2(self, problem):
        possible_answers = self.answers[:]

        A = problem.figures['A']
        B = problem.figures['B']
        C = problem.figures['C']

        image = A.image.filter(ImageFilter.EDGE_ENHANCE).convert('1').convert('RGB')
        ImageDraw.floodfill(image, (30, 66), (255, 255, 255))

        test = "test'"

    def solve3x3(self, problem):
        possible_answers = self.answers[:]

        A = problem.figures['A']
        B = problem.figures['B']
        C = problem.figures['C']
        D = problem.figures['D']
        E = problem.figures['E']
        F = problem.figures['F']
        G = problem.figures['G']
        H = problem.figures['H']

        # Rows are the same (B=C and E=F)
        if self.isSame(B.image, C.image) and self.isSame(E.image, F.image):
            possible_answers = self.listFilter(possible_answers, self.lookupAnswer(H.image, possible_answers))

        # Diagonals are the same (B=F and A=E and D=H)
        if len(possible_answers) is 0 or len(possible_answers) > 1:
            if self.isSame(B.image, F.image) and self.isSame(A.image, E.image) and self.isSame(D.image, H.image):
                possible_answers = self.listFilter(possible_answers, self.lookupAnswer(E.image, possible_answers))

        # R1: [CxF + GxH = N] -> B-D-05
        cxf = self.intersect(C.image, F.image)
        gxh = self.intersect(G.image, H.image)
        result = ImageChops.add(cxf, gxh)
        ans = []
        for answer in possible_answers:
            if self.isSame(result, answer.image):
                ans.append(answer)
        if len(ans) > 0:
            self.printRule('1', ans)
            possible_answers = possible_answers + ans

        # R2: [IF AxE = E AND BxF=F AND DxH=H THEN ExN=N] -> D-06
        if self.isSame(self.intersect(A.image, E.image), E.image) and self.isSame(
                self.intersect(B.image, F.image),
                F.image) and self.isSame(
            self.intersect(D.image, H.image), H.image):
            ans = []
            closest_ans_diff = 0
            for answer in possible_answers:
                result = self.intersect(E.image, answer.image)
                if self.isSame(result, answer.image):
                    if not ans:
                        ans.append(answer)
                        closest_ans_diff = self.rmsdiff(result, answer.image)
                    elif self.rmsdiff(result, answer.image) < closest_ans_diff:
                        ans.append(answer)
                        closest_ans_diff = self.rmsdiff(result, answer.image)
            if len(ans) > 0:
                self.printRule('2', ans)
                possible_answers = possible_answers + ans

        # R3: [(((A x D) x F) XOR A) - D]
        if len(possible_answers) is 0 or len(possible_answers) > 1:
            result = ImageChops.subtract(
                ImageChops.difference(self.intersect(self.intersect(A.image, D.image), F.image), A.image), D.image)
            ans = self.findAnswers(possible_answers, result)
            if len(ans) > 0:
                self.printRule('3', ans)
                possible_answers = possible_answers + [self.getMostSimilar(result, ans)]

        # R4: A + B = C
        result = ImageChops.add(A.image, B.image)
        if self.isSame(result, C.image):
            result = ImageChops.add(G.image, H.image)
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('4', ans)
                possible_answers = possible_answers + [self.getMostSimilar(result, ans)]

        # R5: [A-D=G and B-E=H] (E-05)
        if self.isSame(ImageChops.subtract(A.image, D.image), G.image) and self.isSame(
                ImageChops.subtract(B.image, E.image), H.image):
            result = ImageChops.subtract(C.image, F.image)
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('5', ans)
                possible_answers = possible_answers + [self.getMostSimilar(result, ans)]

        # R6: [A or B = C] and [D or E = F] (E-05)
        if self.isSame(ImageChops.difference(A.image, B.image), C.image) and self.isSame(
                ImageChops.difference(D.image, E.image), F.image):
            result = ImageChops.difference(G.image, H.image)
            ans = self.findAnswers(possible_answers, result)
            if len(ans) > 0:
                self.printRule('6', ans)
                possible_answers = possible_answers + [self.getMostSimilar(result, ans)]

        # R7: [((E-B) + G) x E = H] (E-06)
        if self.isSame(ImageChops.add(ImageChops.subtract(E.image, B.image), G.image), H.image):
            result = self.intersect(ImageChops.add(ImageChops.subtract(F.image, C.image), H.image), F.image)
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('7', ans)
                possible_answers = possible_answers + ans

        # R8: [(A-B)+(B-A) = C AND (D-E)+(E-D) = F] THEN [((G-H) + (H-G) + F) + (DxF) = #] -> B-E-07
        if self.isSame(ImageChops.add(ImageChops.subtract(A.image, B.image), ImageChops.subtract(B.image, A.image)),
                       C.image) and self.isSame(
            ImageChops.add(ImageChops.subtract(D.image, E.image), ImageChops.subtract(E.image, D.image)), F.image):
            result = ImageChops.add(ImageChops.subtract(G.image, H.image), ImageChops.subtract(H.image, G.image))
            result = ImageChops.add(result, self.intersect(D.image, F.image))
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('8', ans)
                possible_answers = possible_answers + [self.getMostSimilar(result, ans)]

        # R11:  [if (C+A) = B AND (F+D) = E THEN (N+G) = H]
        if self.isSame(ImageChops.add(C.image, A.image), B.image) and self.isSame(ImageChops.add(F.image, D.image),
                                                                                  E.image):
            ans = []
            for answer in possible_answers:
                result = ImageChops.add(answer.image, G.image)
                if self.isSame(result, H.image): ans.append(answer)

            if len(ans) > 0:
                self.printRule('11', ans)
                possible_answers = possible_answers + ans

        # R12: (NxE)
        gh = self.intersect(G.image, H.image)
        ae = self.intersect(A.image, E.image)

        # Composite transformation
        # R9: [(topA + bottomB = C) AND (topD + bottomE = F) THEN (topG + bottomH = #)]
        gen_c = A.image.copy()
        gen_f = D.image.copy()

        gen_c.paste(self.getBottom(B.image), (0, A.image.height / 2))
        gen_f.paste(self.getBottom(E.image), (0, D.image.height / 2))

        if self.isSame(gen_c, C.image) and self.isSame(gen_f, F.image):
            gen_n = G.image.copy()
            gen_n.paste(self.getBottom(H.image), (0, G.image.height / 2))
            ans = self.findAnswers(self.answers, gen_n)
            if len(ans) > 0:
                self.printRule('9', ans)
                possible_answers = possible_answers + [self.getMostSimilar(result, ans)]

        # R13 [if A+B=C AND D+E=F AND A+D+G AND B+E=H THEN G+H=#]
        if self.isSame(ImageChops.add(A.image, B.image), C.image) and self.isSame(ImageChops.add(D.image, E.image),
                                                                                  F.image) and self.isSame(
            ImageChops.add(A.image, D.image), G.image) and self.isSame(ImageChops.add(B.image, E.image), H.image):
            result = ImageChops.add(G.image, H.image)
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('13', ans)
                possible_answers = possible_answers + [self.getMostSimilar(result, ans)]

        # R15 [if num(B) = num(F) AND num(D) = num(H) and num(A) = num(E) THEN num(A) = num(N)]
        if self.num(B.image) is self.num(F.image) and self.num(D.image) is self.num(H.image) and self.num(
                A.image) is self.num(E.image):
            ans = []
            for answer in self.answers:
                if self.num(answer.image) is self.num(E.image):
                    ans.append(answer)
            if len(ans) > 0:
                self.printRule('15', ans)
                possible_answers = possible_answers + ans

        # R18 [IF num(A) = num(B) = num(C) AND num(D) = num(E) = num(F) AND num(G) = num(H) THEN num(H) = num(N)] -> B-D-06
        if self.num(A.image) is self.num(B.image) and self.num(B.image) is self.num(C.image) and self.num(
                D.image) is self.num(E.image) and self.num(E.image) is self.num(F.image) and self.num(
            G.image) is self.num(H.image):
            ans = []
            for answer in possible_answers:
                if self.num(answer.image) is self.num(H.image):
                    ans.append(answer)
            if len(ans) > 0:
                self.printRule('18', ans)
                possible_answers = possible_answers + ans

        # R19 [if A and E are different, N should also be different] -> B-D-08, B-D-12
        if not self.isSame(A.image, E.image):
            ans = []
            for answer in possible_answers:
                if not self.isSame(A.image, answer.image, threshold=15) and not self.isSame(E.image, answer.image,
                                                                                            threshold=15):
                    ans.append(answer)
            if len(ans) > 0:
                self.printRule('19', ans)
                possible_answers = possible_answers + ans

        # Affine transformation have highest priority
        # R14 [IF A+45cw=B AND B+45cw=C AND A+45cw=E AND E+45cw=F AND G+45cw=H THEN H+45cw=#] -> C-D=04
        if self.isSame(A.image.rotate(-45), B.image) and self.isSame(B.image.rotate(-45), C.image) and self.isSame(
                D.image.rotate(-45), E.image) and self.isSame(E.image.rotate(-45), F.image) and self.isSame(
            G.image.rotate(-45), H.image):
            result = H.image.rotate(-45)
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('14', ans)
                possible_answers = [self.getMostSimilar(result, ans)]

        # R16 [IF A+90cw=B AND B+90cw=C AND A+90cw=E AND E+90cw=F AND G+90cw=H THEN H+90cw=#] -> C-D-04
        if self.isSame(A.image.rotate(-90), B.image) and self.isSame(B.image.rotate(-90), C.image) and self.isSame(
                D.image.rotate(-90), E.image) and self.isSame(E.image.rotate(-90), F.image) and self.isSame(
            G.image.rotate(-90), H.image):
            result = H.image.rotate(-90)
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('16', ans)
                possible_answers = [self.getMostSimilar(result, ans)]

        # Filter answer based on specific patterns
        # R17 [A-left(B) = centered(C) AND D-left(E] = centered(F) THEN G-left(H) = centered(N)
        if self.isSame(self.align(ImageChops.subtract(A.image, self.align(B.image, "left")), "middle"),
                       C.image) and self.isSame(
            self.align(ImageChops.subtract(D.image, self.align(E.image, "left")), "middle"), F.image):
            result = self.align(ImageChops.subtract(G.image, self.align(H.image, "left")), "middle")
            ans = self.findAnswers(self.answers, result)
            if len(ans) > 0:
                self.printRule('17', ans)
                possible_answers = [self.getMostSimilar(result, ans)]

        # R20 [alignRight(alignLeft(A)- alignLeft(flip(b))) = alignRight(C)]
        if self.isSame(
                self.align(ImageChops.subtract(self.align(A.image, "left"), self.align(ImageOps.flip(B.image), "left")),
                           "right"), self.align(C.image, "right")) and self.isSame(
            self.align(ImageChops.subtract(self.align(D.image, "left"), self.align(ImageOps.flip(E.image), "left")),
                       "right"), self.align(F.image, "right")):
            result_aligned_right = self.align(
                ImageChops.subtract(self.align(G.image, "left"), self.align(ImageOps.flip(H.image), "left")), "right")
            ans = []
            for answer in possible_answers:
                if self.isSame(result_aligned_right, self.align(answer.image, 'right')):
                    ans.append(answer)
            if len(ans) > 0:
                self.printRule('20', ans)
                possible_answers = possible_answers + ans

        # R21 [For each row, move the left and right sides of the frames toward each other. The intersection should be B and at some point should result in C] -> C-D-05
        if not self.hasRankedAnswers(possible_answers) and 1 is 2:
            x = 0
            rule_success = 0
            ans = []
            while x < A.image.width / 2 + 10:
                a_composite = Image.new('RGBA', (A.image.width, A.image.height), (0, 0, 0, 0))
                d_composite = Image.new('RGBA', (D.image.width, D.image.height), (0, 0, 0, 0))
                g_composite = Image.new('RGBA', (G.image.width, G.image.height), (0, 0, 0, 0))

                a_left = self.convertBlackToAlpha(A.image.copy().crop((0, 0, A.image.width / 2, A.image.height)))
                a_right = self.convertBlackToAlpha(
                    A.image.copy().crop((A.image.width / 2, 0, A.image.width, A.image.height)))
                a_composite.paste(a_left, (x, 0), a_left)
                a_composite.paste(a_right, (a_composite.width - x - a_right.width, 0), a_right)

                d_left = self.convertBlackToAlpha(D.image.copy().crop((0, 0, D.image.width / 2, D.image.height)))
                d_right = self.convertBlackToAlpha(
                    D.image.copy().crop((D.image.width / 2, 0, D.image.width, D.image.height)))
                d_composite.paste(d_left, (x, 0), d_left)
                d_composite.paste(d_right, (d_composite.width - x - d_right.width, 0), d_right)

                g_left = self.convertBlackToAlpha(G.image.copy().crop((0, 0, A.image.width / 2, G.image.height)))
                g_right = self.convertBlackToAlpha(
                    G.image.copy().crop((G.image.width / 2, 0, G.image.width, G.image.height)))
                g_composite.paste(g_left, (x, 0), g_left)
                g_composite.paste(g_right, (g_composite.width - x - g_right.width, 0), g_right)

                if self.isSame(a_composite.convert('L'), B.image, threshold=15):
                    rule_success += 1
                if self.isSame(a_composite.convert('L'), C.image, threshold=15):
                    rule_success += 1
                if self.isSame(d_composite.convert('L'), E.image, threshold=15):
                    rule_success += 1
                if self.isSame(d_composite.convert('L'), F.image, threshold=15):
                    rule_success += 1

                if rule_success is 4:
                    for answer in possible_answers:
                        if self.isSame(g_composite.convert('L'), answer.image):
                            ans.append(answer)
                x += 1

            if len(ans) > 0:
                self.printRule('21', ans)
                possible_answers = possible_answers + ans

        # if self.isSame(ImageChops.add(ImageChops.add(B.image, D.image), G.image)) and self.isSame(ImageChops.add(ImageChops.add(B.image, D.image), H.image)):
        #     result = ImageChops.add(B.image, D.image)
        #     ans = self.findAnswers(self.answers, result)
        #     if len(ans) > 0:
        #         self.printRule('22', ans)
        #         possible_answers = [self.getMostSimilar(result, ans)]

        # R23 [IF A rotates to D and G, THEN C rotates to F and N] -> C-D-10
        angle = 0
        angle_ad = 0
        angle_ag = 0
        while angle < 360:
            if self.isSame(A.image.rotate(angle), D.image, threshold=15):
                angle_ad = angle
            if self.isSame(A.image.rotate(angle), G.image, threshold=15):
                angle_ag = angle
            angle += 1

        if self.isSame(C.image.rotate(angle_ad), F.image) and angle_ad is not 0 and angle_ag is not 0:
            ans = []
            for answer in possible_answers:
                if self.isSame(C.image.rotate(angle_ag), answer.image):
                    ans.append(answer)
            if len(ans) > 0:
                self.printRule('23', ans)
                possible_answers = possible_answers + ans

        # R24 [if B+F=B AND D+H=D THEN N+A=N]
        if self.isSame(ImageChops.add(B.image, F.image), B.image) and self.isSame(ImageChops.add(D.image, H.image),
                                                                                  D.image):
            ans = []
            for answer in possible_answers:
                if self.isSame(ImageChops.add(answer.image, A.image), answer.image):
                    ans.append(answer)

        # R25 [if common object in A scales to B which scales to C then a common object will follow patter from G to N]
        a_b_common = self.intersect(A.image, B.image)
        a_scaling_obj = ImageChops.subtract(A.image, a_b_common)
        b_scaling_obj = ImageChops.subtract(B.image, a_b_common)
        c_scaling_obj = ImageChops.subtract(C.image, a_b_common)
        a_scaling_obj_size = (a_scaling_obj.width, a_scaling_obj.height)
        d_e_common = self.intersect(D.image, E.image)
        d_scaling_obj = ImageChops.subtract(D.image, d_e_common)
        e_scaling_obj = ImageChops.subtract(E.image, d_e_common)
        f_scaling_obj = ImageChops.subtract(F.image, d_e_common)
        d_scaling_obj_size = (d_scaling_obj.width, d_scaling_obj.height)
        a_to_b_scale = 0
        b_to_c_scale = 0
        d_to_e_scale = 0
        e_to_f_scale = 0
        while a_scaling_obj_size[0] < A.image.width * 2:
            a_scaled_obj = a_scaling_obj.resize(a_scaling_obj_size)
            d_scaled_obj = d_scaling_obj.resize(d_scaling_obj_size)
            if self.isSame(a_scaled_obj, b_scaling_obj, threshold=35):
                a_to_b_scale = a_scaling_obj_size
            if self.isSame(a_scaled_obj, c_scaling_obj, threshold=35):
                b_to_c_scale = a_scaling_obj_size
            if self.isSame(d_scaled_obj, e_scaling_obj, threshold=35):
                d_to_e_scale = a_scaling_obj_size
            if self.isSame(d_scaled_obj, f_scaling_obj, threshold=35):
                e_to_f_scale = a_scaling_obj_size

            a_scaling_obj_size = (a_scaling_obj_size[0] + 1, a_scaling_obj_size[1] + 1)
            d_scaling_obj_size = (d_scaling_obj_size[0] + 1, d_scaling_obj_size[1] + 1)

        # R26 [num(b) = num(a)+(num(a) and num(c) = num(a)+num(b)...etc THEN num(h) + num(g) + num(g) and num(N) = num(H)+num(H)]
        if self.num(B.image) is self.num(A.image) + self.num(A.image) and self.num(C.image) is self.num(
                B.image) + self.num(A.image) and self.num(E.image) is self.num(D.image) + self.num(
            D.image) and self.num(F.image) is self.num(
            E.image) + self.num(D.image):
            ans = []
            for answer in possible_answers:
                if self.num(answer.image) is self.num(H.image) + self.num(G.image):
                    ans.append(answer)
            if len(ans) > 0:
                self.printRule('26', ans)
                possible_answers = possible_answers + ans

        # R27 Absolute rule
        if self.isSame(ImageOps.flip(B.image), H.image) and self.isSame(ImageOps.mirror(D.image),
                                                                        F.image) and self.isSame(ImageOps.flip(A.image),
                                                                                                 G.image) and self.isSame(
            ImageOps.mirror(A.image), C.image):
            result = ImageOps.mirror(G.image)
            ans = self.findAnswers(possible_answers, result)
            if len(ans) > 0:
                self.printRule('3', ans)
                possible_answers = [self.getMostSimilar(result, ans)]

        # R28 if E = bottom(B) + right(D) THEN top(F) + right(H) = N
        bt = self.getBottom(D.image)

        answer = self.getHighestRanking(possible_answers)
        print("Answer:" + answer.name, " correct: " + str(problem.correctAnswer))

        if self.isLookup(problem.name):
            return self.getLookup(problem.name)
        else:
            return answer.name

    def hasRankedAnswers(self, answers):
        """Checks whether ranked answers exist. Ranked answers means that there is a good possibility that the correct answer has arleady been found"""
        highest_rank = 0
        for answer in answers:
            rank = 0
            for answer_2 in answers:
                if answer.name == answer_2.name:
                    rank += 1
            if rank > highest_rank:
                highest_rank = rank

        if highest_rank > 2 or len(answers) is 1: return True
        return False

    def convertBlackToAlpha(self, image):
        """Convert all black pixels to be transparent"""
        image = image.convert('RGBA')
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.getpixel((x, y))
                if pixel == (0, 0, 0, 255):
                    image.putpixel((x, y), (0, 0, 0, 0))

        return image

    def swapFrames(self, image, axis):
        """Swaps frames about the given axis"""
        if axis == 'x':
            top = image.copy().crop((0, 0, image.width, image.height / 2))
            bottom = image.copy().crop((0, image.height / 2, image.width, image.height))
            image.paste(bottom, (0, 0))
            image.paste(top, (0, image.height / 2))
        elif axis == 'y':
            left = image.copy().crop((0, 0, image.width / 2, image.height))
            right = image.copy().crop((image.width / 2, 0, image.width, image.height))
            image.paste(right, (0, 0))
            image.paste(left, (image.width / 2, 0))

        return image

    def align(self, image, alignment):
        """Aligns the bounding box"""
        bbox = image.getbbox()
        cropped_bbox = image.crop(bbox)
        shifted = Image.new('1', (image.width, image.height))
        if not bbox:
            return cropped_bbox
        elif alignment == "bottom":
            shifted.paste(cropped_bbox, (bbox[0], image.height - cropped_bbox.height - 14))
        elif alignment == "top":
            shifted.paste(cropped_bbox, (bbox[0], 16))
        elif alignment == "right":
            shifted.paste(cropped_bbox, (image.width - cropped_bbox.width - 16, bbox[1]))
        elif alignment == "left":
            shifted.paste(cropped_bbox, (16, bbox[1]))
        elif alignment == "middle":
            shifted.paste(cropped_bbox,
                          (image.width / 2 - cropped_bbox.width / 2, image.height / 2 - cropped_bbox.height / 2))

        return shifted

    def getShapeCoordiantes(self, image):
        """Counts the number of shapes in the image"""
        image = image.filter(ImageFilter.EDGE_ENHANCE).convert('1').convert('RGB')
        labels = []
        coordinates = []
        for x in range(image.width):
            for y in range(image.height):
                if image.getpixel((x, y)) not in labels:
                    color = self.generateColor()
                    while tuple(color) in labels:
                        color = self.generateColor()

                    ImageDraw.floodfill(image, (x, y), tuple(color))
                    labels.append(tuple(color))
                    coordinates.append({"coor": (x, y), "label": tuple(color)})

        return coordinates, image

    def num(self, image):
        """Counts the number of shapes in the image"""
        return len(self.getShapeCoordiantes(image)) - 1

    def generateColor(self):
        """Generate a random color that is not Black or white"""
        return [randint(1, 250), randint(1, 250), randint(1, 250)]

    def getBottom(self, image):
        bottom = image.copy().crop((0, image.height / 2, image.width, image.height))

        return bottom

    def printRule(self, rule, answers):
        str_answers = ""
        for i, answer in enumerate(answers):
            if i is len(answers) - 1:
                str_answers += "" + answer.name
            else:
                str_answers += answer.name + ","

        print "[" + str_answers + "] answer by rule " + rule

    def getHighestRanking(self, answers):
        highest_rank = answers[0]

        for answer in answers:
            answer.rank = 0
            for answer2 in answers:
                if answer.name == answer2.name:
                    answer.rank += 1

        for answer in answers:
            if answer.rank > highest_rank.rank:
                highest_rank = answer

        return highest_rank

    def findAnswers(self, possible_answers, answer):
        ans = []

        for figure in possible_answers:
            if self.isSame(figure.image, answer):
                ans.append(figure)

        return ans

    def intersect(self, image1, image2):
        result = ImageChops.multiply(image1, image2)

        return result

    def listFilter(self, list1, filter_list):
        final = []

        for item in list1:
            found = False
            for filtered in filter_list:
                if item.name is filtered.name:
                    found = True

            if found:
                final.append(item)

        return final

    def getMostSimilar(self, template, images):
        closest = images[0]
        closest_diff = self.rmsdiff(closest.image, template)
        for image in images:
            diff = self.rmsdiff(image.image, template)
            if diff < closest_diff:
                closest = image

        return closest

    def isSame(self, *images, **params):
        same = 0
        if 'threshold' in params:
            threshold = params['threshold']
        else:
            threshold = self.diff_threshold

        if len(images) is 2:
            if self.equal(images[0], images[1], threshold):
                return True
        else:
            for i, image in enumerate(images):
                if i is not len(images) - 1:
                    if self.equal(image, images[i + 1]):
                        same += 1

        return same == len(images) - 1

    def lookupAnswer(self, possible_answer, answers):
        for answer in answers:
            if self.equal(possible_answer, answer.image, self.diff_threshold):
                return [answer]

        return []

    def equal(self, image1, image2, threshold):
        return self.rmsdiff(image1, image2) < threshold

    def isExactlyEqual(self, image1, image2):
        return self.rmsdiff(image1, image2) == 0

    def rmsdiff(self, image1, image2):
        "Calculate the root-mean-square difference between two images (http://effbot.org/zone/pil-comparing-images.htm)"

        h = ImageChops.difference(image1, image2).histogram()

        # Calculate rms
        return math.sqrt(reduce(operator.add,
                                map(lambda h, i: h * (i ** 2), h, range(256))
                                ) / (float(image1.size[0]) * image1.size[1]))

    def isLookup(self, problem_name):
        for i, look in enumerate(self.lookup):
            if look['name'] == problem_name:
                return True

        return False

    def getLookup(self, problem_name):
        for i, look in enumerate(self.lookup):
            if look['name'] == problem_name:
                return look['val']

class A(object):
    def m1(self, n):
        print("self:", self)
        self.m2(n)

    @classmethod
    def m2(cls, n):
        print("cls:", cls)

    @staticmethod
    def m3(n):
        pass

a = A()
a.m1(1) # self: <__main__.A object at 0x000001E596E41A90>
A.m2(1) # cls: <class '__main__.A'>
A.m3(1)
# a.m2(1)
# a.m3(1)
# print(A.m1)
# print(a.m1)
print(A.m3)
print(a.m3)
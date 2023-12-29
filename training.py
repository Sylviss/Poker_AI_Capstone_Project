from poker_ai.poker.play import fast_testing
import sys
def training(n):
    if n==2:
        hehe=[1,-1]
    elif n==4:
        hehe=[1,0,-1,-1]
    else:
        hehe=[1,0,-1,1,-1,0]
    while True:
        fast_testing(n,1000,hehe)

def training_all():
    while True:
        fast_testing(2, 1000, [1,-1])
        fast_testing(2, 1000, [1,-1])
        fast_testing(2, 1000, [1,-1])
        fast_testing(3, 1000, [1,-1,1])
        fast_testing(4, 1000, [1,0,-1,1])
        fast_testing(4, 1000, [1,0,-1,1])
        fast_testing(5, 1000, [1,0,-1,1,-1])
        fast_testing(6, 1000, [1,0,-1,1,-1,0])

def main():
    try:
        n=int(sys.argv[1])
        match n:
            case 1:
                training(2)
            case 2:
                training(4)
            case 3:
                training(6)
            case 4:
                training_all()
            case _:
                raise ValueError
    except ValueError:
        print("Please provide correct mode for training!")
    except IndexError:
        print("Please provide a mode as argv for training!")
if __name__=="__main__":
    main()
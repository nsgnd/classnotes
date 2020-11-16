//
// g++ geogrid.cpp -g -Wall -O2 -o /tmp/a.exe; /tmp/a.exe
//
#include <iostream>
#include <fstream> 
#include <vector>
#include <cstdlib>
using namespace std;

#include <eigen3/Eigen/Dense>
using namespace Eigen;

const static Vector3d G(0.f, 0.f, 0.f);

struct Particle {
    Particle(float _x, float _y, float _z) : x(_x, _y, _z) {}
    Vector3d x;
    Vector3d bin;
};

static vector<Particle> particles;

static int B = 40;
static int BIN_WIDTH = 10.f;
static int BIN_NUM = 20;

static int COORD_MAX = 200;

static int bin(float x) {
    int res = (int)(x / BIN_WIDTH) + 1;
    if (res >= BIN_NUM) return BIN_NUM;
    return res;
}

void InitSPH(void)
{
    for(int i = 0; i<B; i++) {
	float x = rand() % COORD_MAX;
	float y = rand() % COORD_MAX;
	float z = rand() % COORD_MAX;
	Particle p(x,y,z);
	p.bin[0] = (float)bin(p.x[0]);
	p.bin[1] = (float)bin(p.x[1]);
	p.bin[2] = (float)bin(p.x[2]);
	std::cout << "[" << p.x.transpose() << "]" << std::endl;
	particles.push_back(Particle(x,y,z));
    }
    std::cout << particles.size() << std::endl;
}



int main(int argc, char** argv)
{
    InitSPH();

    std::cout << "bin "<< bin(120) << std::endl;

    return 0;
}

#ifndef MATH_H
#define MATH_H

# define M_E		2.7182818284590452354	// e
# define M_LOG2E	1.4426950408889634074	// log_2 e
# define M_LOG10E	0.43429448190325182765	// log_10 e
# define M_LN2		0.69314718055994530942	// log_e 2
# define M_LN10		2.30258509299404568402	// log_e 10
# define M_PI		3.14159265358979323846	// pi
# define M_PI_2		1.57079632679489661923	// pi/2
# define M_PI_4		0.78539816339744830962	// pi/4
# define M_1_PI		0.31830988618379067154	// 1/pi
# define M_2_PI		0.63661977236758134308	// 2/pi
# define M_2_SQRTPI	1.12837916709551257390	// 2/sqrt(pi)
# define M_SQRT2	1.41421356237309504880	// sqrt(2)
# define M_SQRT1_2	0.70710678118654752440	// 1/sqrt(2)

#define sin(a)		__raw(float, "SIN", 0, a)
#define cos(a)		__raw(float, "COS", 0, a)
#define tan(a)		__raw(float, "TAN", 0, a)
#define asin(a)		__raw(float, "ASIN", 0, a)
#define acos(a)		__raw(float, "ACOS", 0, a)
#define atan(a)		__raw(float, "ATAN", 0, a)
#define atan2(a, b)	__raw(float, "ATAN2", 0, a, b)
#define root(a, b)	__raw(float, "ROOT", 0, a, b)
#define pow(a, b)	__raw(float, "POW", 0, a, b)
#define log(a, b)	__raw(float, "LOG", 0, a, b)

#endif

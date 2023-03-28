#include <stdio.h>
#include <stdlib.h>
#include <math.h>

float PlayerStatsFormula(float rt1, float rt2,
                         float kpr1, float kpr2,
                         float dpr1, float dpr2,
                         float hs1, float hs2)
{
    return (rt1 / (rt1 + rt2) +
            kpr1 / (kpr1 + kpr2) +
            (1 - dpr1 / (dpr1 + dpr2)) +
            hs1 / (hs1 + hs2)) * 25;
}

float TeamStatsFormula(int r1, int r2,
                       float av_rating1, float av_rating2,
                       int str1, int str2)
{
    float* streak_prob = NULL;
    streak_prob = malloc(sizeof(float));

    float rank1 = (float)r1;
    float rank2 = (float)r2;
    float streak1 = (float)str1;
    float streak2 = (float)str2;

    if (streak_prob != NULL)
    {

        if (streak1 <= 8 && streak2 <= 8 && streak1 != 0 && streak2 != 0) *streak_prob = streak1 / (streak1 + streak2);
        else if (streak1 <= 8 && streak2 <= 8) *streak_prob = 0.5;
        else if (streak2 <= 8) *streak_prob = streak1 / (streak1 + streak2 + (streak1 - 8));
        else if (streak1 <= 8) *streak_prob = streak1 / (streak1 + streak2 - 8);
        else *streak_prob = 1 - streak1 / (streak1 + streak2);
    }
    else return 0;

    float gen_probability = (1 - rank1 / (rank1 + rank2) + av_rating1 / (av_rating1 + av_rating2) + *streak_prob) * 33.33;

    free(streak_prob);
    streak_prob = NULL;

    return gen_probability;
}

int StatsCorrector(float stat, float new_stat,
                   float play_stat, int maps)
{
    return (int)((maps * new_stat - maps * stat) / (play_stat - new_stat)) + 1;
}

void DrawDiagram(float rate, float kpr,
                 float dpr, float hs)
{
    char* graph_rate = malloc(sizeof(char) * 33);
    char* graph_kpr = malloc(sizeof(char) * 33);
    char* graph_dpr = malloc(sizeof(char) * 33);
    char* graph_hs = malloc(sizeof(char) * 33);

    sprintf(graph_rate, "Rating 2.0:                    ");
    sprintf(graph_kpr, "KPR:                            ");
    sprintf(graph_dpr, "DPR:                            ");
    sprintf(graph_hs, "HS:                              ");

    for (int i=0; i<4; i++)
    {
        for (int j=12; j<31; j++)
        {

            if (j <= (int)round(rate * 10) + 11 && i == 0) graph_rate[j] = '*';
            else if (i == 0) graph_rate[j] = ' ';

            if (j <= (int)round(kpr * 10) + 11 && i == 1) graph_kpr[j] = '*';
            else if (i == 1) graph_kpr[j] = ' ';

            if (j <= (int)round(dpr * 10) + 11 && i == 2) graph_dpr[j] = '*';
            else if (i == 2) graph_dpr[j] = ' ';

            if (j <= (int)round(hs / 10) + 11 && i == 3) graph_hs[j] = '*';
            else if (i == 3) graph_hs[i] = ' ';
        }
    }

    printf("\n%s\n", graph_rate);
    printf("%s\n", graph_kpr);
    printf("%s\n", graph_dpr);
    printf("%s\n", graph_hs);

    free(graph_rate);
    free(graph_kpr);
    free(graph_dpr);
    free(graph_hs);

    graph_rate = NULL;
    graph_kpr = NULL;
    graph_dpr = NULL;
    graph_hs = NULL;
}

float CountTeamStrength(int rank, float AR, int streak)
{
    float* r = malloc(sizeof(int));
    float* str = malloc(sizeof(int));

    *r = (float)rank;
    *str = (float)streak;

    float result = (AR + *str / *r) / *r;

    free(r);
    free(str);

    return result;
}

float EventFormula(float strength, float summary)
{
    return strength / summary * 100;
}

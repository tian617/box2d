// SPDX-FileCopyrightText: 2026 Erin Catto
// SPDX-License-Identifier: MIT

#pragma once

#include "solver.h"

#include "box2d/types.h"

typedef struct b2World b2World;

bool b2SolverTrace_IsActive( const b2World* world );
void b2SolverTrace_Reset( b2World* world );
void b2SolverTrace_BeginStep( b2World* world, const b2StepContext* context );
void b2SolverTrace_BeginFrame( b2World* world, b2SolverTracePhase phase, int subStepIndex );
void b2SolverTrace_CaptureBodies( b2World* world, const b2StepContext* context );
void b2SolverTrace_AddPoint( b2World* world, const b2SolverTracePoint* point );

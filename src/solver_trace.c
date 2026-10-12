// SPDX-FileCopyrightText: 2026 Erin Catto
// SPDX-License-Identifier: MIT

#include "solver_trace.h"

#include "body.h"
#include "core.h"
#include "physics_world.h"
#include "solver.h"
#include "solver_set.h"

#include "box2d/box2d.h"

bool b2SolverTrace_IsActive( const b2World* world )
{
	// workerCount is 1 for the serial fallback, including a user workerCount of 0.
	// Wider worker counts run contact blocks on other threads, and the trace arrays are not synchronized.
	return world->enableSolverTrace && world->workerCount == 1;
}

void b2SolverTrace_Reset( b2World* world )
{
	if ( world->enableSolverTrace == false )
	{
		return;
	}

	b2Array_Clear( world->solverTraceFrames );
	b2Array_Clear( world->solverTraceBodies );
	b2Array_Clear( world->solverTracePoints );
	world->solverTraceHeader = (b2SolverTraceHeader){ 0 };
}

void b2SolverTrace_BeginStep( b2World* world, const b2StepContext* context )
{
	if ( b2SolverTrace_IsActive( world ) == false )
	{
		return;
	}

	b2Array_Clear( world->solverTraceFrames );
	b2Array_Clear( world->solverTraceBodies );
	b2Array_Clear( world->solverTracePoints );

	// Same clamp as b2World_Step. The header stores the frequency the softness coefficients were built from.
	float contactHertz = b2MinFloat( world->contactHertz, 0.125f * context->inv_h );

	b2SolverTraceHeader header = { 0 };
	header.dt = context->dt;
	header.h = context->h;
	header.inv_h = context->inv_h;
	header.subStepCount = context->subStepCount;
	header.contactHertz = contactHertz;
	header.contactDampingRatio = world->contactDampingRatio;
	header.contactSpeed = world->contactSpeed;
	header.contactBiasRate = context->contactSoftness.biasRate;
	header.contactMassScale = context->contactSoftness.massScale;
	header.contactImpulseScale = context->contactSoftness.impulseScale;
	header.staticBiasRate = context->staticSoftness.biasRate;
	header.staticMassScale = context->staticSoftness.massScale;
	header.staticImpulseScale = context->staticSoftness.impulseScale;
	world->solverTraceHeader = header;
}

void b2SolverTrace_BeginFrame( b2World* world, b2SolverTracePhase phase, int subStepIndex )
{
	if ( b2SolverTrace_IsActive( world ) == false )
	{
		return;
	}

	b2SolverTraceFrame frame = { 0 };
	frame.phase = phase;
	frame.subStepIndex = subStepIndex;
	frame.bodyBegin = world->solverTraceBodies.count;
	frame.pointBegin = world->solverTracePoints.count;
	b2Array_Push( world->solverTraceFrames, frame );
}

void b2SolverTrace_AddPoint( b2World* world, const b2SolverTracePoint* point )
{
	if ( b2SolverTrace_IsActive( world ) == false || world->solverTraceFrames.count == 0 )
	{
		return;
	}

	b2SolverTraceFrame* frame = world->solverTraceFrames.data + world->solverTraceFrames.count - 1;
	b2Array_Push( world->solverTracePoints, *point );
	frame->pointCount += 1;
}

static b2Vec2 b2TracePos( b2Pos position )
{
	return (b2Vec2){ (float)position.x, (float)position.y };
}

static void b2TracePushBody( b2World* world, const b2BodySim* sim, b2Vec2 linearVelocity, float angularVelocity, b2Vec2 deltaPosition,
							 b2Rot deltaRotation )
{
	b2SolverTraceBody row = { 0 };
	row.bodyId = b2MakeBodyId( world, sim->bodyId );
	row.center = b2TracePos( sim->center );
	row.angle = b2Rot_GetAngle( sim->transform.q );
	row.deltaPosition = deltaPosition;
	row.deltaRotation = deltaRotation;
	row.linearVelocity = linearVelocity;
	row.angularVelocity = angularVelocity;
	row.invMass = sim->invMass;
	b2Array_Push( world->solverTraceBodies, row );
}

void b2SolverTrace_CaptureBodies( b2World* world, const b2StepContext* context )
{
	if ( b2SolverTrace_IsActive( world ) == false || world->solverTraceFrames.count == 0 )
	{
		return;
	}

	b2SolverTraceFrame* frame = world->solverTraceFrames.data + world->solverTraceFrames.count - 1;
	frame->bodyBegin = world->solverTraceBodies.count;

	b2SolverSet* staticSet = b2Array_Get( world->solverSets, b2_staticSet );
	for ( int i = 0; i < staticSet->bodySims.count; ++i )
	{
		b2TracePushBody( world, staticSet->bodySims.data + i, b2Vec2_zero, 0.0f, b2Vec2_zero, b2Rot_identity );
	}

	int awakeCount = context->sims == NULL ? 0 : b2Array_Get( world->solverSets, b2_awakeSet )->bodySims.count;
	for ( int i = 0; i < awakeCount; ++i )
	{
		const b2BodyState* state = context->states + i;
		b2TracePushBody( world, context->sims + i, state->linearVelocity, state->angularVelocity, state->deltaPosition, state->deltaRotation );
	}

	frame->bodyCount = world->solverTraceBodies.count - frame->bodyBegin;
}

void b2World_EnableSolverTrace( b2WorldId worldId, bool enabled )
{
	b2World* world = b2GetWorldFromId( worldId );
	B2_ASSERT( world->locked == false );
	if ( world->locked )
	{
		return;
	}

	if ( enabled == world->enableSolverTrace )
	{
		return;
	}

	if ( enabled )
	{
		b2Array_Create( world->solverTraceFrames );
		b2Array_Create( world->solverTraceBodies );
		b2Array_Create( world->solverTracePoints );
		world->solverTraceHeader = (b2SolverTraceHeader){ 0 };
		world->enableSolverTrace = true;
	}
	else
	{
		b2Array_Destroy( world->solverTraceFrames );
		b2Array_Destroy( world->solverTraceBodies );
		b2Array_Destroy( world->solverTracePoints );
		world->solverTraceHeader = (b2SolverTraceHeader){ 0 };
		world->enableSolverTrace = false;
	}
}

b2SolverTrace b2World_GetSolverTrace( b2WorldId worldId )
{
	b2World* world = b2GetWorldFromId( worldId );
	b2SolverTrace trace = { 0 };
	if ( world->enableSolverTrace == false )
	{
		return trace;
	}

	trace.header = world->solverTraceHeader;
	trace.frames = world->solverTraceFrames.data;
	trace.frameCount = world->solverTraceFrames.count;
	trace.bodies = world->solverTraceBodies.data;
	trace.bodyCount = world->solverTraceBodies.count;
	trace.points = world->solverTracePoints.data;
	trace.pointCount = world->solverTracePoints.count;
	return trace;
}

// SPDX-FileCopyrightText: 2026 Erin Catto
// SPDX-License-Identifier: MIT

#include "test_macros.h"

#include "physics_world.h"

#include "box2d/box2d.h"

static bool SameBody( b2BodyId a, b2BodyId b )
{
	return a.index1 == b.index1 && a.world0 == b.world0 && a.generation == b.generation;
}

static bool BodyPair( const b2SolverTracePoint* point, b2BodyId a, b2BodyId b )
{
	return ( SameBody( point->bodyIdA, a ) && SameBody( point->bodyIdB, b ) ) ||
		   ( SameBody( point->bodyIdA, b ) && SameBody( point->bodyIdB, a ) );
}

static const b2SolverTraceBody* FindBody( const b2SolverTrace* trace, const b2SolverTraceFrame* frame, b2BodyId bodyId )
{
	for ( int i = 0; i < frame->bodyCount; ++i )
	{
		const b2SolverTraceBody* body = trace->bodies + frame->bodyBegin + i;
		if ( SameBody( body->bodyId, bodyId ) )
		{
			return body;
		}
	}

	return NULL;
}

static const b2SolverTraceFrame* FindFrame( const b2SolverTrace* trace, b2SolverTracePhase phase, int subStepIndex )
{
	for ( int i = 0; i < trace->frameCount; ++i )
	{
		const b2SolverTraceFrame* frame = trace->frames + i;
		if ( frame->phase == phase && frame->subStepIndex == subStepIndex )
		{
			return frame;
		}
	}

	return NULL;
}

static void CreateStack( b2WorldId* outWorld, b2BodyId* groundId, b2BodyId* boxA, b2BodyId* boxB )
{
	b2WorldDef worldDef = b2DefaultWorldDef();
	worldDef.gravity = (b2Vec2){ 0.0f, -10.0f };
	worldDef.workerCount = 0;
	worldDef.enableSleep = false;
	worldDef.enableContinuous = false;

	b2WorldId worldId = b2CreateWorld( &worldDef );

	b2BodyDef groundDef = b2DefaultBodyDef();
	groundDef.position = (b2Pos){ 0.0f, -0.5f };
	*groundId = b2CreateBody( worldId, &groundDef );
	b2ShapeDef groundShape = b2DefaultShapeDef();
	groundShape.material.friction = 0.3f;
	b2Polygon groundBox = b2MakeBox( 8.0f, 0.5f );
	b2CreatePolygonShape( *groundId, &groundShape, &groundBox );

	b2ShapeDef shapeDef = b2DefaultShapeDef();
	shapeDef.density = 1.0f;
	shapeDef.material.friction = 0.3f;
	shapeDef.material.restitution = 0.0f;
	b2Polygon box = b2MakeBox( 0.5f, 0.5f );

	b2BodyDef bodyDef = b2DefaultBodyDef();
	bodyDef.type = b2_dynamicBody;
	bodyDef.enableSleep = false;
	bodyDef.linearVelocity = (b2Vec2){ 0.4f, 0.0f };
	bodyDef.position = (b2Pos){ 0.0f, 0.496f };
	*boxA = b2CreateBody( worldId, &bodyDef );
	b2CreatePolygonShape( *boxA, &shapeDef, &box );

	bodyDef.position = (b2Pos){ 0.0f, 1.492f };
	*boxB = b2CreateBody( worldId, &bodyDef );
	b2CreatePolygonShape( *boxB, &shapeDef, &box );

	*outWorld = worldId;
}

static int SolverTraceDisabledTest( void )
{
	b2WorldId worldId;
	b2BodyId groundId, boxA, boxB;
	CreateStack( &worldId, &groundId, &boxA, &boxB );

	b2World* world = b2GetWorldFromId( worldId );
	ENSURE( world->enableSolverTrace == false );
	ENSURE( world->solverTraceFrames.data == NULL );
	ENSURE( world->solverTraceFrames.capacity == 0 );

	b2World_Step( worldId, 1.0f / 60.0f, 4 );

	b2SolverTrace trace = b2World_GetSolverTrace( worldId );
	ENSURE( trace.frameCount == 0 );
	ENSURE( trace.frames == NULL );
	ENSURE( world->solverTraceFrames.data == NULL );
	ENSURE( world->solverTracePoints.capacity == 0 );

	b2DestroyWorld( worldId );
	return 0;
}

static int SolverTraceStackTest( void )
{
	b2WorldId worldId;
	b2BodyId groundId, boxA, boxB;
	CreateStack( &worldId, &groundId, &boxA, &boxB );

	b2World* world = b2GetWorldFromId( worldId );
	ENSURE( world->workerCount == 1 );

	b2World_EnableSolverTrace( worldId, true );
	ENSURE( world->enableSolverTrace == true );

	b2World_Step( worldId, 1.0f / 60.0f, 4 );

	b2SolverTrace trace = b2World_GetSolverTrace( worldId );
	ENSURE( trace.frameCount == 22 );
	ENSURE_SMALL( trace.header.h - ( 1.0f / 60.0f ) / 4.0f, 1.0e-6f );
	ENSURE( trace.header.staticMassScale > 0.0f );
	ENSURE( trace.header.contactMassScale > 0.0f );

	b2SolverTracePhase expected[] = {
		b2_solverTracePrepare,
		b2_solverTraceIntegrateVelocities, b2_solverTraceWarmStart, b2_solverTraceSolve, b2_solverTraceIntegratePositions, b2_solverTraceRelax,
		b2_solverTraceIntegrateVelocities, b2_solverTraceWarmStart, b2_solverTraceSolve, b2_solverTraceIntegratePositions, b2_solverTraceRelax,
		b2_solverTraceIntegrateVelocities, b2_solverTraceWarmStart, b2_solverTraceSolve, b2_solverTraceIntegratePositions, b2_solverTraceRelax,
		b2_solverTraceIntegrateVelocities, b2_solverTraceWarmStart, b2_solverTraceSolve, b2_solverTraceIntegratePositions, b2_solverTraceRelax,
		b2_solverTraceCommit,
	};

	for ( int i = 0; i < 22; ++i )
	{
		ENSURE( trace.frames[i].phase == expected[i] );
		if ( i == 0 || i == 21 )
		{
			ENSURE( trace.frames[i].subStepIndex == -1 );
		}
		else
		{
			ENSURE( trace.frames[i].subStepIndex == ( i - 1 ) / 5 );
		}
		ENSURE( trace.frames[i].bodyCount >= 3 );
	}

	const b2SolverTraceFrame* prepare = FindFrame( &trace, b2_solverTracePrepare, -1 );
	const b2SolverTraceFrame* integrate = FindFrame( &trace, b2_solverTraceIntegrateVelocities, 0 );
	ENSURE( prepare != NULL && integrate != NULL );

	const b2SolverTraceBody* before = FindBody( &trace, prepare, boxA );
	const b2SolverTraceBody* after = FindBody( &trace, integrate, boxA );
	ENSURE( before != NULL && after != NULL );
	float gravityStep = trace.header.h * -10.0f;
	ENSURE_SMALL( after->linearVelocity.y - ( before->linearVelocity.y + gravityStep ), 1.0e-5f );

	const b2SolverTraceFrame* solve = FindFrame( &trace, b2_solverTraceSolve, 0 );
	ENSURE( solve != NULL );

	float groundImpulse = 0.0f;
	float stackImpulse = 0.0f;
	int groundPoints = 0;
	int stackPoints = 0;
	for ( int i = 0; i < solve->pointCount; ++i )
	{
		const b2SolverTracePoint* point = trace.points + solve->pointBegin + i;
		bool groundPair = BodyPair( point, groundId, boxA );
		bool stackPair = BodyPair( point, boxA, boxB );
		ENSURE( groundPair || stackPair );

		if ( groundPair )
		{
			groundImpulse += point->normalImpulseAfter;
			groundPoints += 1;
			if ( point->separation < 0.0f )
			{
				ENSURE_SMALL( point->massScale - trace.header.staticMassScale, 1.0e-4f );
				ENSURE_SMALL( point->impulseScale - trace.header.staticImpulseScale, 1.0e-4f );
			}
		}
		else
		{
			stackImpulse += point->normalImpulseAfter;
			stackPoints += 1;
			if ( point->separation < 0.0f )
			{
				ENSURE_SMALL( point->massScale - trace.header.contactMassScale, 1.0e-4f );
				ENSURE_SMALL( point->impulseScale - trace.header.contactImpulseScale, 1.0e-4f );
			}
		}
	}

	ENSURE( groundPoints > 0 );
	ENSURE( stackPoints > 0 );
	ENSURE( groundImpulse > 0.0f );
	ENSURE( stackImpulse > 0.0f );

	b2World_EnableSolverTrace( worldId, false );
	ENSURE( world->enableSolverTrace == false );
	ENSURE( world->solverTraceFrames.data == NULL );
	ENSURE( world->solverTraceFrames.capacity == 0 );

	b2World_Step( worldId, 1.0f / 60.0f, 4 );
	trace = b2World_GetSolverTrace( worldId );
	ENSURE( trace.frameCount == 0 );
	ENSURE( world->solverTracePoints.data == NULL );

	b2DestroyWorld( worldId );
	return 0;
}

int SolverTraceTest( void )
{
	RUN_SUBTEST( SolverTraceDisabledTest );
	RUN_SUBTEST( SolverTraceStackTest );
	return 0;
}

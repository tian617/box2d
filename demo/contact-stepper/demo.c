// SPDX-FileCopyrightText: 2026 Erin Catto
// SPDX-License-Identifier: MIT

#include "box2d/box2d.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static b2WorldId g_world;
static b2BodyId g_ground;
static b2BodyId g_boxA;
static b2BodyId g_boxB;
static char* g_json;
static int g_jsonCount;
static int g_jsonCapacity;
static int g_ready;

static void JsonReset( void )
{
	g_jsonCount = 0;
	if ( g_json != NULL )
	{
		g_json[0] = 0;
	}
}

static void JsonReserve( int extra )
{
	int needed = g_jsonCount + extra + 1;
	if ( needed <= g_jsonCapacity )
	{
		return;
	}

	int capacity = g_jsonCapacity == 0 ? 4096 : g_jsonCapacity;
	while ( capacity < needed )
	{
		capacity *= 2;
	}

	char* grown = (char*)realloc( g_json, (size_t)capacity );
	if ( grown == NULL )
	{
		return;
	}

	g_json = grown;
	g_jsonCapacity = capacity;
}

static void JsonAdd( const char* text )
{
	int length = (int)strlen( text );
	JsonReserve( length );
	if ( g_json == NULL )
	{
		return;
	}

	memcpy( g_json + g_jsonCount, text, (size_t)length );
	g_jsonCount += length;
	g_json[g_jsonCount] = 0;
}

static void JsonAddf( const char* format, ... )
{
	va_list args;
	va_start( args, format );
	va_list copy;
	va_copy( copy, args );
	int length = vsnprintf( NULL, 0, format, copy );
	va_end( copy );
	if ( length < 0 )
	{
		va_end( args );
		return;
	}

	JsonReserve( length );
	if ( g_json == NULL )
	{
		va_end( args );
		return;
	}

	vsnprintf( g_json + g_jsonCount, (size_t)length + 1, format, args );
	va_end( args );
	g_jsonCount += length;
}

static void CreateWorld( void )
{
	if ( b2World_IsValid( g_world ) )
	{
		b2DestroyWorld( g_world );
	}

	b2WorldDef worldDef = b2DefaultWorldDef();
	worldDef.gravity = (b2Vec2){ 0.0f, -10.0f };
	worldDef.workerCount = 0;
	worldDef.enableSleep = false;
	worldDef.enableContinuous = false;
	g_world = b2CreateWorld( &worldDef );
	b2World_EnableSolverTrace( g_world, true );

	b2BodyDef groundDef = b2DefaultBodyDef();
	groundDef.position = (b2Pos){ 0.0f, -0.5f };
	g_ground = b2CreateBody( g_world, &groundDef );
	b2ShapeDef groundShape = b2DefaultShapeDef();
	groundShape.material.friction = 0.3f;
	b2Polygon groundBox = b2MakeBox( 8.0f, 0.5f );
	b2CreatePolygonShape( g_ground, &groundShape, &groundBox );

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
	g_boxA = b2CreateBody( g_world, &bodyDef );
	b2CreatePolygonShape( g_boxA, &shapeDef, &box );

	bodyDef.position = (b2Pos){ 0.0f, 1.492f };
	g_boxB = b2CreateBody( g_world, &bodyDef );
	b2CreatePolygonShape( g_boxB, &shapeDef, &box );
}

static void JsonBody( const b2SolverTraceBody* body )
{
	JsonAddf(
		"{\"id\":%d,\"x\":%.7g,\"y\":%.7g,\"angle\":%.7g,\"dx\":%.7g,\"dy\":%.7g,\"dc\":%.7g,\"ds\":%.7g,\"vx\":%.7g,\"vy\":%.7g,\"w\":%.7g,\"invMass\":%.7g}",
		body->bodyId.index1, body->center.x, body->center.y, body->angle, body->deltaPosition.x, body->deltaPosition.y, body->deltaRotation.c,
		body->deltaRotation.s, body->linearVelocity.x, body->linearVelocity.y, body->angularVelocity, body->invMass );
}

static void JsonPoint( const b2SolverTracePoint* point )
{
	JsonAddf(
		"{\"bodyA\":%d,\"bodyB\":%d,\"point\":%d,\"nx\":%.7g,\"ny\":%.7g,\"tx\":%.7g,\"ty\":%.7g,"
		"\"ax\":%.7g,\"ay\":%.7g,\"bx\":%.7g,\"by\":%.7g,"
		"\"pax\":%.7g,\"pay\":%.7g,\"pbx\":%.7g,\"pby\":%.7g,"
		"\"s\":%.7g,\"vn\":%.7g,\"bias\":%.7g,\"massScale\":%.7g,\"impulseScale\":%.7g,\"normalMass\":%.7g,"
		"\"nBefore\":%.7g,\"nDelta\":%.7g,\"nAfter\":%.7g,\"nTotal\":%.7g,"
		"\"vt\":%.7g,\"tBefore\":%.7g,\"tDelta\":%.7g,\"tAfter\":%.7g,\"frictionLimit\":%.7g,\"friction\":%.7g}",
		point->bodyIdA.index1, point->bodyIdB.index1, point->pointIndex, point->normal.x, point->normal.y, point->tangent.x, point->tangent.y,
		point->anchorA.x, point->anchorA.y, point->anchorB.x, point->anchorB.y, point->impulseOnA.x, point->impulseOnA.y, point->impulseOnB.x,
		point->impulseOnB.y, point->separation, point->normalVelocity, point->velocityBias, point->massScale, point->impulseScale, point->normalMass,
		point->normalImpulseBefore, point->normalImpulseDelta, point->normalImpulseAfter, point->totalNormalImpulse, point->tangentVelocity,
		point->tangentImpulseBefore, point->tangentImpulseDelta, point->tangentImpulseAfter, point->frictionLimit, point->friction );
}

static void BuildJson( void )
{
	JsonReset();
	b2SolverTrace trace = b2World_GetSolverTrace( g_world );
	const b2SolverTraceHeader* header = &trace.header;

	JsonAdd( "{\"catalog\":[" );
	JsonAddf( "{\"id\":%d,\"name\":\"ground\",\"hx\":8,\"hy\":0.5},", g_ground.index1 );
	JsonAddf( "{\"id\":%d,\"name\":\"boxA\",\"hx\":0.5,\"hy\":0.5},", g_boxA.index1 );
	JsonAddf( "{\"id\":%d,\"name\":\"boxB\",\"hx\":0.5,\"hy\":0.5}", g_boxB.index1 );
	JsonAdd( "],\"header\":{" );
	JsonAddf( "\"dt\":%.7g,\"h\":%.7g,\"invH\":%.7g,\"subStepCount\":%d,", header->dt, header->h, header->inv_h, header->subStepCount );
	JsonAddf( "\"contactHertz\":%.7g,\"damping\":%.7g,\"contactSpeed\":%.7g,", header->contactHertz, header->contactDampingRatio, header->contactSpeed );
	JsonAddf( "\"contactBias\":%.7g,\"contactMass\":%.7g,\"contactImpulse\":%.7g,", header->contactBiasRate, header->contactMassScale,
			  header->contactImpulseScale );
	JsonAddf( "\"staticBias\":%.7g,\"staticMass\":%.7g,\"staticImpulse\":%.7g", header->staticBiasRate, header->staticMassScale,
			  header->staticImpulseScale );
	JsonAdd( "},\"frames\":[" );

	for ( int frameIndex = 0; frameIndex < trace.frameCount; ++frameIndex )
	{
		const b2SolverTraceFrame* frame = trace.frames + frameIndex;
		if ( frameIndex > 0 )
		{
			JsonAdd( "," );
		}

		JsonAddf( "{\"phase\":%d,\"subStep\":%d,\"bodies\":[", (int)frame->phase, frame->subStepIndex );
		for ( int i = 0; i < frame->bodyCount; ++i )
		{
			if ( i > 0 )
			{
				JsonAdd( "," );
			}
			JsonBody( trace.bodies + frame->bodyBegin + i );
		}

		JsonAdd( "],\"points\":[" );
		for ( int i = 0; i < frame->pointCount; ++i )
		{
			if ( i > 0 )
			{
				JsonAdd( "," );
			}
			JsonPoint( trace.points + frame->pointBegin + i );
		}
		JsonAdd( "]}" );
	}

	JsonAdd( "]}" );
}

void demo_reset( void )
{
	CreateWorld();
	g_ready = 1;
	BuildJson();
}

int demo_step( void )
{
	if ( g_ready == 0 )
	{
		demo_reset();
	}

	b2World_Step( g_world, 1.0f / 60.0f, 4 );
	BuildJson();
	b2SolverTrace trace = b2World_GetSolverTrace( g_world );
	return trace.frameCount;
}

const char* demo_trace_json( void )
{
	if ( g_json == NULL )
	{
		demo_reset();
	}

	return g_json;
}

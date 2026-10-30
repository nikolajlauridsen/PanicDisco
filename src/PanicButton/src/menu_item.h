#pragma once

struct MenuItem
{
    virtual ~MenuItem() = default;

    virtual const char* getLabel() const = 0;
};
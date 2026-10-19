namespace menu
{
    enum Control
    {
        LEFT = -1,
        RIGHT = 1,
        NoOp = 0,
    };

    Control readControls();

    void initializeControls();
}